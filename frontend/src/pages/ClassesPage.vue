<template>
  <q-page padding>
    <div class="row items-center q-mb-sm">
      <div class="text-h5 col">Turmas</div>
      <q-space />
      <q-input v-model="search" placeholder="Pesquisar..." dense outlined clearable style="min-width:200px">
        <template #prepend><q-icon name="search" /></template>
      </q-input>
      <q-btn color="primary" icon="add" label="Nova" @click="openCreate" class="q-ml-sm" />
      <q-btn color="secondary" icon="upload" label="Importar Turmas" @click="showImport = true" class="q-ml-sm" />
    </div>

    <!-- Filters: school and year level -->
    <div class="row items-center q-mb-md q-gutter-xs">
      <div class="text-caption text-grey-6 q-mr-xs">Escola:</div>
      <q-chip
        v-for="school in schoolsStore.schools" :key="school.id"
        clickable
        :color="filterSchoolId === school.id ? 'primary' : 'grey-3'"
        :text-color="filterSchoolId === school.id ? 'white' : 'dark'"
        dense
        @click="filterSchoolId = filterSchoolId === school.id ? null : school.id"
      >{{ school.name }}</q-chip>
      <q-separator vertical class="q-mx-sm" />
      <div class="text-caption text-grey-6 q-mr-xs">Ano:</div>
      <q-chip
        v-for="yl in availableYearLevels" :key="yl"
        clickable
        :color="filterYearLevel === yl ? 'secondary' : 'grey-3'"
        :text-color="filterYearLevel === yl ? 'white' : 'dark'"
        dense
        @click="filterYearLevel = filterYearLevel === yl ? null : yl"
      >{{ yl }}.º</q-chip>
    </div>

    <ImportDialog
      v-model="showImport"
      title="Importar Turmas"
      endpoint="/imports/classes"
      :extra-params="{ school_id: selectedSchoolId, academic_year_id: selectedYearId }"
      entity-type="classes"
      @done="classesStore.fetchAll()"
    />

    <q-table :rows="filteredClasses" :columns="columns" row-key="id" :loading="classesStore.loading" :filter="search" sort-by="name">
      <template #body-cell-notes="props">
        <q-td :props="props">
          <span v-if="props.row.notes" class="text-caption text-grey-8">
            <q-icon name="info" size="xs" color="info" class="q-mr-xs" />{{ props.row.notes }}
          </span>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn unelevated size="sm" color="secondary" icon="call_split" label="Turnos" @click="openGroups(props.row)" class="q-mr-xs">
            <q-tooltip>Gerir grupos/turnos de disciplinas simultâneas desta turma</q-tooltip>
          </q-btn>
          <q-btn unelevated size="sm" color="grey-6" icon="edit" label="Editar" @click="openEdit(props.row)" class="q-mr-xs" />
          <q-btn unelevated size="sm" color="negative" icon="delete" label="Apagar" @click="confirmDelete(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Class dialog -->
    <q-dialog v-model="dialog">
      <q-card style="min-width: 450px">
        <q-card-section><div class="text-h6">{{ editing ? 'Editar' : 'Nova' }} Turma</div></q-card-section>
        <q-card-section>
          <q-form @submit="save">
            <q-select v-model="form.school_id" :options="schoolOptions" label="Escola *" emit-value map-options :rules="[v => !!v || 'Obrigatório']" />
            <q-select v-model="form.academic_year_id" :options="yearOptions" label="Ano Letivo *" emit-value map-options :rules="[v => !!v || 'Obrigatório']" />
            <q-input v-model="form.name" label="Nome da turma *" :rules="[v => !!v || 'Obrigatório']" />
            <q-input v-model.number="form.year_level" label="Ano de escolaridade *" type="number" min="1" />
            <q-input v-model.number="form.num_students" label="Nº de alunos" type="number" min="1" />
            <q-input v-model="form.notes" label="Observações" clearable hint="Ex: info de articulado, condições especiais" />
            <div class="row justify-end q-mt-md q-gutter-sm">
              <q-btn flat label="Cancelar" v-close-popup />
              <q-btn type="submit" color="primary" :label="editing ? 'Guardar' : 'Criar'" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Groups/Turnos dialog -->
    <q-dialog v-model="groupsDialog" full-width>
      <q-card style="max-width:860px;width:100%">
        <q-card-section class="row items-center bg-secondary text-white">
          <div>
            <div class="text-h6"><q-icon name="call_split" class="q-mr-sm" />Turnos — {{ selectedClass?.name }}</div>
            <div class="text-caption opacity-80">Cada turno define duas disciplinas que decorrem ao mesmo tempo, em salas e com professores diferentes</div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <!-- Curriculum read-only — redirects to plans for editing -->
          <q-banner dense rounded class="bg-blue-1 text-blue-10 q-mb-md">
            <template #avatar><q-icon name="menu_book" color="blue-7" /></template>
            Para adicionar, editar ou remover disciplinas desta turma, usa
            <router-link to="/curriculum-plans" class="text-blue-9 text-weight-medium" @click="groupsDialog = false">
              Planos Curriculares
            </router-link>.
            A lista abaixo é apenas de consulta.
          </q-banner>

          <div class="text-subtitle2 q-mb-xs text-grey-8">Disciplinas desta turma</div>
          <div v-if="curriculumEntries.length === 0" class="text-caption text-grey-5 q-mb-md q-py-sm">
            Nenhuma disciplina atribuída — aplica um plano curricular primeiro.
          </div>
          <div v-else class="row q-gutter-xs q-mb-md flex-wrap">
            <q-chip
              v-for="e in curriculumEntries" :key="e.id"
              dense square size="sm"
              color="grey-2" text-color="dark"
            >
              {{ subjectName(e.subject_id) }}
              <span class="text-grey-6 q-ml-xs">{{ e.hours_per_week }}h</span>
              <q-badge v-if="e.is_semestral" :color="e.semester === 1 ? 'blue-7' : 'orange-7'"
                class="q-ml-xs" :label="e.semester === 1 ? '1.ºS' : '2.ºS'" />
            </q-chip>
          </div>

          <q-separator class="q-mb-md" />

          <!-- Subject groups / turnos -->
          <div class="row items-center q-mb-sm">
            <div class="col">
              <div class="text-subtitle2">Turnos definidos</div>
              <div class="text-caption text-grey-6">Metade da turma tem a disciplina da esquerda enquanto a outra metade tem a da direita</div>
            </div>
            <q-btn color="secondary" icon="add" size="sm" label="Novo turno" unelevated @click="openNewGroupDialog" />
          </div>

          <div v-if="subjectGroups.length === 0" class="text-caption text-grey-6 q-py-md text-center">
            <q-icon name="call_split" size="lg" color="grey-4" class="q-mb-xs block" />
            Nenhum turno definido.<br>
            Exemplo: CN e FQ em laboratório — metade da turma tem CN enquanto a outra tem FQ.
          </div>

          <q-list v-else bordered separator class="rounded-borders">
            <q-item v-for="group in subjectGroups" :key="group.id" class="q-py-sm">
              <q-item-section>
                <div v-if="group.name" class="text-caption text-weight-medium text-grey-7 q-mb-xs">
                  <q-icon name="call_split" size="xs" color="secondary" class="q-mr-xs" />{{ group.name }}
                </div>
                <div class="row items-center q-gutter-sm">
                  <!-- 1.ª metade -->
                  <q-card flat bordered class="col q-pa-sm" style="min-width:120px">
                    <div class="text-caption text-grey-6 q-mb-xs">1.ª metade</div>
                    <div v-if="group.entries[0]" class="text-body2 text-weight-medium text-secondary">
                      {{ entrySubjectName(group.entries[0].curriculum_entry_id) }}
                    </div>
                    <div v-else class="text-caption text-grey-4 text-italic">sem disciplina</div>
                  </q-card>
                  <!-- separador simultâneo -->
                  <div class="col-auto text-center text-grey-5 q-px-xs">
                    <q-icon name="swap_horiz" size="sm" /><br>
                    <span class="text-caption" style="font-size:10px">simultâneo</span>
                  </div>
                  <!-- 2.ª metade -->
                  <q-card flat bordered class="col q-pa-sm" style="min-width:120px">
                    <div class="text-caption text-grey-6 q-mb-xs">2.ª metade</div>
                    <div v-if="group.entries[1]" class="text-body2 text-weight-medium text-secondary">
                      {{ entrySubjectName(group.entries[1].curriculum_entry_id) }}
                    </div>
                    <div v-else class="text-caption text-grey-4 text-italic">sem disciplina</div>
                  </q-card>
                </div>
              </q-item-section>
              <q-item-section side top>
                <q-btn flat round size="sm" color="negative" icon="delete" @click="deleteGroup(group.id)">
                  <q-tooltip>Apagar turno</q-tooltip>
                </q-btn>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- New group dialog -->
    <q-dialog v-model="newGroupDialog">
      <q-card style="min-width: 440px">
        <q-card-section class="bg-secondary text-white row items-center">
          <div>
            <div class="text-h6"><q-icon name="call_split" class="q-mr-sm" />Novo Turno</div>
            <div class="text-caption opacity-80">As duas disciplinas ocorrem ao mesmo tempo, com professores e salas diferentes</div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="newGroupForm.name"
            label="Nome do turno (opcional)"
            hint='Ex: "Turno Lab", "CN / FQ"'
            clearable
          />
          <div>
            <div class="text-caption text-grey-7 q-mb-xs">1.ª metade da turma</div>
            <q-select
              v-model="newGroupForm.entry1"
              :options="availableEntriesForNew"
              label="Disciplina A *"
              emit-value map-options
            />
          </div>
          <div>
            <div class="text-caption text-grey-7 q-mb-xs">2.ª metade da turma — ocorre ao mesmo tempo que A</div>
            <q-select
              v-model="newGroupForm.entry2"
              :options="availableEntriesForNew2"
              label="Disciplina B *"
              emit-value map-options
              :disable="!newGroupForm.entry1"
              :hint="!newGroupForm.entry1 ? 'Seleciona primeiro a Disciplina A' : ''"
            />
          </div>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="secondary" icon="add" label="Criar Turno"
            @click="createGroup"
            :disable="!newGroupForm.entry1 || !newGroupForm.entry2"
            :loading="creatingGroup"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useClassesStore, type SchoolClass, type CurriculumEntry } from 'stores/classes'
import { useSchoolsStore } from 'stores/schools'
import { useAcademicYearsStore } from 'stores/academicYears'
import { useSubjectsStore } from 'stores/subjects'
import { api } from 'boot/axios'
import ImportDialog from 'components/ImportDialog.vue'

const $q = useQuasar()
const classesStore = useClassesStore()
const schoolsStore = useSchoolsStore()
const yearsStore = useAcademicYearsStore()
const subjectsStore = useSubjectsStore()

const search = ref('')
const showImport = ref(false)
const filterSchoolId = ref<number | null>(null)
const filterYearLevel = ref<number | null>(null)
const selectedSchoolId = computed(() => schoolsStore.schools[0]?.id ?? null)
const selectedYearId = computed(() => yearsStore.years.find((y) => y.is_active)?.id ?? yearsStore.years[0]?.id ?? null)

const availableYearLevels = computed(() => {
  const yls = new Set(classesStore.classes.map((c) => c.year_level))
  return Array.from(yls).sort((a, b) => a - b)
})

const filteredClasses = computed(() => {
  return classesStore.classes.filter((c) => {
    if (filterSchoolId.value !== null && c.school_id !== filterSchoolId.value) return false
    if (filterYearLevel.value !== null && c.year_level !== filterYearLevel.value) return false
    return true
  })
})

const columns = [
  { name: 'name', label: 'Nome', field: 'name', align: 'left' as const, sortable: true },
  { name: 'year_level', label: 'Ano', field: 'year_level', align: 'center' as const },
  { name: 'num_students', label: 'Alunos', field: 'num_students', align: 'center' as const },
  { name: 'notes', label: 'Observações', field: 'notes', align: 'left' as const },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' as const },
]

const dialog = ref(false)
const editing = ref<null | SchoolClass>(null)
const form = ref({ school_id: null as number | null, academic_year_id: null as number | null, name: '', year_level: 5, num_students: 25, notes: '' })

const groupsDialog = ref(false)
const selectedClass = ref<SchoolClass | null>(null)
const curriculumEntries = ref<CurriculumEntry[]>([])

const schoolOptions = computed(() => schoolsStore.schools.map((s) => ({ label: s.name, value: s.id })))
const yearOptions = computed(() => yearsStore.years.map((y) => ({ label: y.name, value: y.id })))

function subjectName(id: number) {
  return subjectsStore.subjects.find((s) => s.id === id)?.name ?? '—'
}

// Subject groups (turnos)
interface SubjectGroupEntry { id: number; group_id: number; curriculum_entry_id: number }
interface SubjectGroupItem { id: number; name: string; academic_year_id: number; entries: SubjectGroupEntry[] }
const subjectGroups = ref<SubjectGroupItem[]>([])

const newGroupDialog = ref(false)
const creatingGroup = ref(false)
const newGroupForm = ref({ name: '', entry1: null as number | null, entry2: null as number | null })

const entriesNotInAnyGroup = computed(() => {
  const inGroup = new Set(subjectGroups.value.flatMap(g => g.entries.map(e => e.curriculum_entry_id)))
  return curriculumEntries.value.filter(e => !inGroup.has(e.id))
})

const availableEntriesForNew = computed(() =>
  entriesNotInAnyGroup.value.map(e => ({ label: subjectName(e.subject_id), value: e.id }))
)

const availableEntriesForNew2 = computed(() =>
  entriesNotInAnyGroup.value
    .filter(e => e.id !== newGroupForm.value.entry1)
    .map(e => ({ label: subjectName(e.subject_id), value: e.id }))
)

function entrySubjectName(curriculum_entry_id: number) {
  const e = curriculumEntries.value.find(e => e.id === curriculum_entry_id)
  return e ? subjectName(e.subject_id) : '?'
}

async function loadSubjectGroups() {
  if (!selectedClass.value) return
  const yearId = selectedClass.value.academic_year_id
  const { data } = await api.get<SubjectGroupItem[]>('/subject-groups', { params: { academic_year_id: yearId } })
  const classEntryIds = new Set(curriculumEntries.value.map(e => e.id))
  subjectGroups.value = data.filter(g => g.entries.some(e => classEntryIds.has(e.curriculum_entry_id)))
}

function openNewGroupDialog() {
  newGroupForm.value = { name: '', entry1: null, entry2: null }
  newGroupDialog.value = true
}

async function createGroup() {
  if (!selectedClass.value || !newGroupForm.value.entry1 || !newGroupForm.value.entry2) return
  creatingGroup.value = true
  try {
    const yearId = selectedClass.value.academic_year_id
    const name = newGroupForm.value.name.trim() || `Turno ${subjectGroups.value.length + 1}`
    const { data: group } = await api.post<SubjectGroupItem>('/subject-groups', { name, academic_year_id: yearId })
    const [r1, r2] = await Promise.all([
      api.post<SubjectGroupEntry>(`/subject-groups/${group.id}/entries`, { curriculum_entry_id: newGroupForm.value.entry1 }),
      api.post<SubjectGroupEntry>(`/subject-groups/${group.id}/entries`, { curriculum_entry_id: newGroupForm.value.entry2 }),
    ])
    group.entries = [r1.data, r2.data]
    subjectGroups.value.push(group)
    newGroupDialog.value = false
  } finally {
    creatingGroup.value = false
  }
}

async function deleteGroup(groupId: number) {
  await api.delete(`/subject-groups/${groupId}`)
  subjectGroups.value = subjectGroups.value.filter(g => g.id !== groupId)
}

onMounted(async () => {
  await Promise.all([
    classesStore.fetchAll(),
    schoolsStore.fetchAll(),
    yearsStore.fetchAll(),
    subjectsStore.fetchAll(),
  ])
})

function openCreate() {
  editing.value = null
  form.value = { school_id: null, academic_year_id: null, name: '', year_level: 5, num_students: 25, notes: '' }
  dialog.value = true
}

function openEdit(row: SchoolClass) {
  editing.value = row
  form.value = { school_id: row.school_id, academic_year_id: row.academic_year_id, name: row.name, year_level: row.year_level, num_students: row.num_students, notes: row.notes ?? '' }
  dialog.value = true
}

async function save() {
  if (!form.value.school_id || !form.value.academic_year_id) return
  try {
    if (editing.value) {
      await classesStore.update(editing.value.id, form.value)
      $q.notify({ type: 'positive', message: 'Atualizada' })
    } else {
      await classesStore.create(form.value as Parameters<typeof classesStore.create>[0])
      $q.notify({ type: 'positive', message: 'Criada' })
    }
    dialog.value = false
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao guardar' })
  }
}

async function openGroups(row: SchoolClass) {
  selectedClass.value = row
  curriculumEntries.value = await classesStore.fetchCurriculum(row.id)
  await loadSubjectGroups()
  groupsDialog.value = true
}

function confirmDelete(row: SchoolClass) {
  $q.dialog({
    title: 'Confirmar eliminação',
    message: `Eliminar "${row.name}"?`,
    ok: { label: 'Eliminar', color: 'negative' },
    cancel: true,
  }).onOk(async () => {
    await classesStore.remove(row.id)
    $q.notify({ type: 'positive', message: 'Eliminada' })
  })
}
</script>
