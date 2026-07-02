"""
Regression tests for scheduler room assignment.

Before the fix, every lesson of a school was assigned rooms_by_school[sid][0],
so all simultaneous classes shared the same room. The scheduler must now:
  1. give simultaneous lessons distinct rooms (no room double-booking);
  2. keep a stable "home room" per class;
  3. let semestral pairs share a room (opposite semesters — no real clash);
  4. give turno (subject-group) lessons in the same slot different rooms.

Run:  cd backend && python -m pytest ../tests/test_room_assignment.py -v
(Uses a throwaway sqlite DB via DATABASE_URL — set before importing app.)
"""
import os
import sys
import tempfile
from collections import defaultdict
from datetime import date, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"

from app import database  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

# Rebind in case app.database was already imported with another URL
database.engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)

from app.models import models  # noqa: E402
from app.scheduler import engine as sched  # noqa: E402

models.Base.metadata.create_all(bind=database.engine)


def _seed_common(db, tag: str, n_rooms: int):
    cluster = models.Cluster(name=f"AG {tag}")
    db.add(cluster); db.flush()
    year = models.AcademicYear(
        cluster_id=cluster.id, name=f"26/27 {tag}", is_active=True,
        start_date=date(2026, 9, 1), end_date=date(2027, 6, 30),
    )
    db.add(year); db.flush()
    school = models.School(cluster_id=cluster.id, name=f"EB {tag}", code=f"EB{tag}")
    db.add(school); db.flush()
    rooms = [models.Room(school_id=school.id, name=f"S{i+1}") for i in range(n_rooms)]
    db.add_all(rooms); db.flush()
    for d in range(5):
        for s in range(1, 5):
            db.add(models.TimeSlotConfig(
                academic_year_id=year.id, day_of_week=d, slot_number=s,
                start_time=time(8, 0), end_time=time(9, 0), is_break=False,
            ))
    db.flush()
    return cluster, year, school


def test_no_room_double_booking_and_stable_home_room():
    db = database.SessionLocal()
    cluster, year, school = _seed_common(db, "T1", n_rooms=3)

    classes = [models.Class(school_id=school.id, academic_year_id=year.id,
                            name=f"5{chr(65+i)}", year_level=5) for i in range(3)]
    db.add_all(classes); db.flush()
    subj_pt = models.Subject(cluster_id=cluster.id, name="PT-T1", code="PT1")
    subj_mat = models.Subject(cluster_id=cluster.id, name="MAT-T1", code="MAT1")
    db.add_all([subj_pt, subj_mat]); db.flush()
    teachers = [models.Teacher(cluster_id=cluster.id, name=f"Prof T1-{i}") for i in range(3)]
    db.add_all(teachers); db.flush()
    for i, cls in enumerate(classes):
        for subj in (subj_pt, subj_mat):
            db.add(models.CurriculumEntry(
                class_id=cls.id, subject_id=subj.id,
                teacher_id=teachers[i].id, hours_per_week=3.0,
            ))
    tt = models.Timetable(academic_year_id=year.id, name="TT-T1", status="pending")
    db.add(tt); db.commit()
    tt_id = tt.id
    class_ids = [c.id for c in classes]
    db.close()

    sched.generate_timetable(tt_id, {"max_time_seconds": 30, "class_ids": class_ids})

    db = database.SessionLocal()
    tt = db.query(models.Timetable).get(tt_id)
    assert tt.status == "generated", tt.generation_log
    lessons = db.query(models.ScheduledLesson).filter_by(timetable_id=tt_id).all()
    assert len(lessons) == 18

    by_room_slot = defaultdict(list)
    for l in lessons:
        assert l.room_id is not None
        by_room_slot[(l.day_of_week, l.slot_number, l.room_id)].append(l.id)
    clashes = {k: v for k, v in by_room_slot.items() if len(v) > 1}
    assert not clashes, f"room double-booking: {clashes}"

    entry_class = {e.id: e.class_id for e in db.query(models.CurriculumEntry).all()}
    class_rooms = defaultdict(set)
    for l in lessons:
        class_rooms[entry_class[l.curriculum_entry_id]].add(l.room_id)
    assert all(len(rs) <= 2 for rs in class_rooms.values()), \
        f"home room not stable: {dict(class_rooms)}"
    db.close()


def test_turnos_get_distinct_rooms_and_semestral_pair_can_share():
    db = database.SessionLocal()
    cluster, year, school = _seed_common(db, "T2", n_rooms=4)

    cls = models.Class(school_id=school.id, academic_year_id=year.id, name="7A", year_level=7)
    db.add(cls); db.flush()
    names = ["TIC", "ET", "CN", "FQ", "PT"]
    subs = {n: models.Subject(cluster_id=cluster.id, name=f"{n}-T2", code=f"{n}2") for n in names}
    db.add_all(subs.values()); db.flush()
    tchs = {n: models.Teacher(cluster_id=cluster.id, name=f"Prof T2-{n}") for n in names}
    db.add_all(tchs.values()); db.flush()

    e_tic = models.CurriculumEntry(class_id=cls.id, subject_id=subs["TIC"].id,
                                   teacher_id=tchs["TIC"].id, hours_per_week=1.0,
                                   is_semestral=True, semester=1)
    e_et = models.CurriculumEntry(class_id=cls.id, subject_id=subs["ET"].id,
                                  teacher_id=tchs["ET"].id, hours_per_week=1.0,
                                  is_semestral=True, semester=2)
    db.add_all([e_tic, e_et]); db.flush()
    e_tic.paired_entry_id = e_et.id
    e_et.paired_entry_id = e_tic.id

    e_cn = models.CurriculumEntry(class_id=cls.id, subject_id=subs["CN"].id,
                                  teacher_id=tchs["CN"].id, hours_per_week=1.0)
    e_fq = models.CurriculumEntry(class_id=cls.id, subject_id=subs["FQ"].id,
                                  teacher_id=tchs["FQ"].id, hours_per_week=1.0)
    e_pt = models.CurriculumEntry(class_id=cls.id, subject_id=subs["PT"].id,
                                  teacher_id=tchs["PT"].id, hours_per_week=3.0)
    db.add_all([e_cn, e_fq, e_pt]); db.flush()

    sg = models.SubjectGroup(name="Turno CN/FQ T2", academic_year_id=year.id)
    db.add(sg); db.flush()
    db.add_all([models.SubjectGroupEntry(group_id=sg.id, curriculum_entry_id=e_cn.id),
                models.SubjectGroupEntry(group_id=sg.id, curriculum_entry_id=e_fq.id)])

    tt = models.Timetable(academic_year_id=year.id, name="TT-T2", status="pending")
    db.add(tt); db.commit()
    tt_id = tt.id
    cn_id, fq_id, tic_id, et_id = e_cn.id, e_fq.id, e_tic.id, e_et.id
    class_ids = [cls.id]
    db.close()

    sched.generate_timetable(tt_id, {"max_time_seconds": 30, "class_ids": class_ids})

    db = database.SessionLocal()
    tt = db.query(models.Timetable).get(tt_id)
    assert tt.status == "generated", tt.generation_log
    lessons = db.query(models.ScheduledLesson).filter_by(timetable_id=tt_id).all()
    by_entry = {l.curriculum_entry_id: l for l in lessons}

    l_tic, l_et = by_entry[tic_id], by_entry[et_id]
    assert (l_tic.day_of_week, l_tic.slot_number) == (l_et.day_of_week, l_et.slot_number)
    assert l_tic.semester == 1 and l_et.semester == 2

    l_cn, l_fq = by_entry[cn_id], by_entry[fq_id]
    if (l_cn.day_of_week, l_cn.slot_number) == (l_fq.day_of_week, l_fq.slot_number):
        assert l_cn.room_id != l_fq.room_id, "simultaneous turno lessons share a room"

    # No annual/annual or same-semester room clash anywhere
    usage = defaultdict(list)
    for l in lessons:
        usage[(l.day_of_week, l.slot_number, l.room_id)].append(l.semester)
    for k, sems in usage.items():
        for i in range(len(sems)):
            for j in range(i + 1, len(sems)):
                a, b = sems[i], sems[j]
                assert not (a is None or b is None or a == b), f"room clash at {k}: {sems}"
    db.close()


if __name__ == "__main__":
    test_no_room_double_booking_and_stable_home_room()
    print("test 1 OK")
    test_turnos_get_distinct_rooms_and_semestral_pair_can_share()
    print("test 2 OK")
