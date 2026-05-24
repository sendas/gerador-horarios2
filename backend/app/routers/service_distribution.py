import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    Teacher, ScheduledLesson, CurriculumEntry, Class, Subject,
    NonTeachingAssignment, Timetable, AcademicYear, TeacherSchoolAssignment, School,
    SubjectGroupEntry,
)

router = APIRouter(prefix="/service-distribution", tags=["service_distribution"])


@router.get("")
def get_service_distribution(
    academic_year_id: int,
    timetable_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    # Resolve the cluster_id from the academic year so we only surface teachers
    # that belong to the same cluster (mirrors the pattern used by other routers).
    year = db.query(AcademicYear).filter(AcademicYear.id == academic_year_id).first()
    cluster_id = year.cluster_id if year else None

    # All timetables for this academic year (for the selector on the frontend)
    timetables_q = db.query(Timetable).filter(
        Timetable.academic_year_id == academic_year_id
    ).order_by(Timetable.name)
    timetables = [{"id": t.id, "name": t.name} for t in timetables_q.all()]

    # Teachers assigned to this academic year via TeacherSchoolAssignment
    assignments_q = (
        db.query(TeacherSchoolAssignment)
        .filter(TeacherSchoolAssignment.academic_year_id == academic_year_id)
        .all()
    )
    teacher_ids = {a.teacher_id for a in assignments_q}
    # Map teacher_id -> primary school (name + id)
    primary_school_map: dict = {}
    for a in assignments_q:
        if a.is_primary or a.teacher_id not in primary_school_map:
            school = db.query(School).filter(School.id == a.school_id).first()
            primary_school_map[a.teacher_id] = {
                "id": a.school_id,
                "name": school.name if school else None,
                "is_primary": bool(a.is_primary),
            }

    # Build unique school list for the filter
    school_ids_seen: set = set()
    schools_list = []
    for info in primary_school_map.values():
        if info["id"] not in school_ids_seen:
            school_ids_seen.add(info["id"])
            schools_list.append({"id": info["id"], "name": info["name"]})
    schools_list.sort(key=lambda s: s["name"] or "")

    # Fallback: all teachers in the cluster when no school assignments exist yet
    if not teacher_ids and cluster_id:
        all_teachers = db.query(Teacher).filter(Teacher.cluster_id == cluster_id).all()
        teacher_ids = {t.id for t in all_teachers}

    teachers_q = (
        db.query(Teacher)
        .filter(Teacher.id.in_(teacher_ids))
        .order_by(Teacher.name)
    )
    teachers = teachers_q.all()

    result = []
    for teacher in teachers:
        # ── Scheduled lessons ────────────────────────────────────────────────
        if timetable_id is not None:
            lessons = (
                db.query(ScheduledLesson)
                .filter(
                    ScheduledLesson.timetable_id == timetable_id,
                    ScheduledLesson.teacher_id == teacher.id,
                )
                .all()
            )
        else:
            lessons = []

        scheduled_hours = len(lessons)

        # ── Classes taught ────────────────────────────────────────────────────
        # Group by (class_id, subject_id) via CurriculumEntry; keep first
        # hours_per_week found for each combination.
        classes_taught_map: dict = {}  # (class_id, subject_id) -> dict
        for lesson in lessons:
            entry: Optional[CurriculumEntry] = lesson.curriculum_entry
            if entry is None:
                continue
            key = (entry.class_id, entry.subject_id)
            if key not in classes_taught_map:
                cls: Optional[Class] = entry.class_
                subj: Optional[Subject] = entry.subject
                classes_taught_map[key] = {
                    "class_name": cls.name if cls else "—",
                    "subject_name": subj.name if subj else "—",
                    "hours_per_week": entry.hours_per_week,
                }

        classes_taught = sorted(
            classes_taught_map.values(),
            key=lambda x: (x["class_name"], x["subject_name"]),
        )

        # ── Non-teaching assignments ──────────────────────────────────────────
        non_teaching_count = (
            db.query(NonTeachingAssignment)
            .filter(
                NonTeachingAssignment.teacher_id == teacher.id,
                NonTeachingAssignment.academic_year_id == academic_year_id,
            )
            .count()
        )

        # ── teaching_component — use the column when it exists, else None ────
        teaching_component = getattr(teacher, "teaching_component", None)

        total_service = scheduled_hours + non_teaching_count

        school_info = primary_school_map.get(teacher.id, {})
        result.append({
            "id": teacher.id,
            "name": teacher.name,
            "teaching_component": teaching_component,
            "scheduled_hours": scheduled_hours,
            "non_teaching_hours": non_teaching_count,
            "total_service": total_service,
            "classes_taught": classes_taught,
            "primary_school_id": school_info.get("id"),
            "primary_school_name": school_info.get("name"),
        })

    return {"teachers": result, "timetables": timetables, "schools": schools_list}


@router.get("/mapa-servico/{teacher_id}")
def get_mapa_servico(
    teacher_id: int,
    academic_year_id: int,
    timetable_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        return {"error": "Professor não encontrado"}

    year = db.query(AcademicYear).filter(AcademicYear.id == academic_year_id).first()

    # Primary school
    primary = (
        db.query(TeacherSchoolAssignment)
        .filter(
            TeacherSchoolAssignment.teacher_id == teacher_id,
            TeacherSchoolAssignment.academic_year_id == academic_year_id,
            TeacherSchoolAssignment.is_primary == True,  # noqa
        )
        .first()
    )
    school = db.query(School).filter(School.id == primary.school_id).first() if primary else None

    # ── Non-teaching rows ─────────────────────────────────────────────────────
    non_teaching_rows = []

    def _parse_role(json_str):
        if not json_str:
            return []
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                if data and isinstance(data[0], str):
                    return [{"role": r, "hours": 1} for r in data]
                return data
        except Exception:
            pass
        return []

    te_roles = _parse_role(getattr(teacher, "te_role", None))
    credit_roles = _parse_role(getattr(teacher, "credit_role", None))
    art79 = getattr(teacher, "art79_reduction", 0) or 0

    # TE roles
    for r in te_roles:
        non_teaching_rows.append({
            "tl": r.get("hours", 1),
            "discipline": r.get("role", "TE"),
            "text": "",
            "type": "TE",
        })

    # Credit roles
    for r in credit_roles:
        non_teaching_rows.append({
            "tl": r.get("hours", 1),
            "discipline": r.get("role", "Crédito"),
            "text": "",
            "type": "CH",
        })

    # Art.79° reduction
    if art79 > 0:
        non_teaching_rows.append({
            "tl": art79,
            "discipline": "Redução Art.79°",
            "text": "",
            "type": "Artº 79",
        })

    # ── Teaching rows ─────────────────────────────────────────────────────────
    teaching_rows = []
    seen_entries: set = set()

    if timetable_id:
        lessons = (
            db.query(ScheduledLesson)
            .filter(
                ScheduledLesson.timetable_id == timetable_id,
                ScheduledLesson.teacher_id == teacher_id,
            )
            .all()
        )
        for lesson in lessons:
            entry: Optional[CurriculumEntry] = lesson.curriculum_entry
            if not entry or entry.id in seen_entries:
                continue
            seen_entries.add(entry.id)

            # Turno: check if entry belongs to a subject group
            sge = (
                db.query(SubjectGroupEntry)
                .filter(SubjectGroupEntry.curriculum_entry_id == entry.id)
                .first()
            )
            turno = f"T{sge.group_id % 10 or 1}" if sge else ""

            room = lesson.room.name if lesson.room else ""
            discipline = entry.teacher_label or (entry.subject.name if entry.subject else "?")
            teaching_rows.append({
                "tl": entry.hours_per_week,
                "class_name": entry.class_.name if entry.class_ else "—",
                "discipline": discipline,
                "turno": turno,
                "semestral": bool(entry.is_semestral),
                "room": room,
                "text": "",
                "description": "Articulado" if entry.paired_entry_id else "",
            })
    else:
        # Without timetable: use CurriculumEntries assigned to this teacher
        entries = (
            db.query(CurriculumEntry)
            .filter(CurriculumEntry.teacher_id == teacher_id)
            .join(Class, CurriculumEntry.class_id == Class.id)
            .filter(Class.academic_year_id == academic_year_id)
            .all()
        )
        for entry in entries:
            sge = (
                db.query(SubjectGroupEntry)
                .filter(SubjectGroupEntry.curriculum_entry_id == entry.id)
                .first()
            )
            turno = f"T{sge.group_id % 10 or 1}" if sge else ""
            discipline = entry.teacher_label or (entry.subject.name if entry.subject else "?")
            teaching_rows.append({
                "tl": entry.hours_per_week,
                "class_name": entry.class_.name if entry.class_ else "—",
                "discipline": discipline,
                "turno": turno,
                "semestral": bool(entry.is_semestral),
                "room": "",
                "text": "",
                "description": "Articulado" if entry.paired_entry_id else "",
            })

    teaching_rows.sort(key=lambda r: (r["class_name"], r["discipline"]))

    total_tl = sum(r["tl"] for r in non_teaching_rows) + sum(r["tl"] for r in teaching_rows)

    return {
        "teacher": {
            "id": teacher.id,
            "name": teacher.name,
            "school_name": school.name if school else None,
            "cluster_name": school.cluster.name if school and school.cluster else None,
        },
        "academic_year_name": year.name if year else "",
        "non_teaching_rows": non_teaching_rows,
        "teaching_rows": teaching_rows,
        "total_tl": total_tl,
    }
