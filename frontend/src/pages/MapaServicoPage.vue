<template>
  <q-page padding class="mapa-servico-page">
    <div class="row items-center q-mb-md">
      <div class="text-h5 col">Mapa de Serviço Docente</div>
    </div>

    <div class="row q-gutter-md" style="align-items: flex-start">
      <!-- ── Left panel: filters + teacher list ──────────────────── -->
      <div style="width: 300px; flex-shrink: 0">
        <q-card flat bordered>
          <q-card-section class="bg-primary text-white q-py-sm">
            <div class="text-subtitle2">Docentes</div>
          </q-card-section>
          <q-card-section class="q-pa-sm">
            <q-select
              v-model="selectedYearId"
              :options="yearOptions"
              option-label="label"
              option-value="value"
              emit-value map-options
              label="Ano letivo"
              dense outlined
              class="q-mb-xs"
              @update:model-value="onYearChange"
            />
            <q-select
              v-model="selectedTimetableId"
              :options="timetableOptions"
              option-label="label"
              option-value="value"
              emit-value map-options
              label="Horário (opcional)"
              dense outlined clearable
              class="q-mb-xs"
              @update:model-value="onTimetableChange"
            />
            <q-select
              v-model="selectedSchoolId"
              :options="schoolOptions"
              option-label="label"
              option-value="value"
              emit-value map-options
              label="Escola"
              dense outlined clearable
              class="q-mb-xs"
            />
            <q-input v-model="search" placeholder="Pesquisar docente..." dense outlined clearable>
              <template #prepend><q-icon name="search" /></template>
            </q-input>
          </q-card-section>
          <q-separator />
          <div v-if="loading" class="flex flex-center q-pa-md">
            <q-spinner color="primary" />
          </div>
          <q-scroll-area v-else style="height: calc(100vh - 360px); min-height: 200px">
            <q-list separator dense>
              <q-item
                v-for="t in filteredTeachers"
                :key="t.id"
                clickable
                :active="selectedTeacherId === t.id"
                active-class="bg-blue-1 text-primary"
                @click="selectTeacher(t)"
              >
                <q-item-section>
                  <q-item-label lines="1">{{ t.name }}</q-item-label>
                  <q-item-label v-if="t.primary_school_name" caption>{{ t.primary_school_name }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="filteredTeachers.length === 0">
                <q-item-section class="text-grey-5 text-caption text-center q-pa-sm">
                  {{ selectedYearId ? 'Nenhum docente encontrado' : 'Selecione um ano letivo' }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-scroll-area>
        </q-card>
      </div>

      <!-- ── Right panel: Mapa de Serviço ────────────────────────── -->
      <div class="col">
        <div v-if="!selectedTeacherId" class="flex flex-center column items-center text-grey-5 q-pa-xl">
          <q-icon name="person_search" size="64px" />
          <div class="text-h6 q-mt-md">Selecione um docente</div>
          <div class="text-caption">Escolha um docente na lista para ver o mapa de serviço</div>
        </div>

        <div v-else-if="mapaLoading" class="flex flex-center q-pa-xl">
          <q-spinner size="xl" color="primary" />
        </div>

        <template v-else-if="mapaData">
          <!-- Action buttons -->
          <div class="row items-center q-mb-md q-gutter-sm">
            <q-btn flat dense icon="print" color="primary" label="Imprimir / PDF" @click="printMapa" />
            <q-btn flat dense icon="download" color="orange-7" label="Guardar HTML" @click="downloadMapa" />
          </div>

          <!-- Header card -->
          <q-card flat bordered class="q-mb-sm">
            <q-card-section class="q-pa-md">
              <div class="row justify-between items-start">
                <div>
                  <div v-if="mapaData.teacher.cluster_name" class="text-subtitle1 text-weight-bold">
                    {{ mapaData.teacher.cluster_name }}
                  </div>
                  <div class="text-body2">{{ mapaData.teacher.school_name }}</div>
                  <div class="text-caption text-grey-7">Horários {{ mapaData.academic_year_name }}</div>
                </div>
                <div class="text-right">
                  <div class="text-h6 text-primary">{{ mapaData.teacher.name }}</div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Mapa table -->
          <q-card flat bordered>
            <q-card-section class="q-pa-sm overflow-auto">
              <table class="mapa-table">
                <thead>
                  <tr>
                    <th style="width:44px">TL</th>
                    <th style="min-width:70px">Turma/s</th>
                    <th>Disciplina</th>
                    <th style="width:60px">Turnos</th>
                    <th style="width:68px">Semestral</th>
                    <th style="width:80px">Sala</th>
                    <th>Texto</th>
                    <th>Descrição</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(r, i) in mapaData.non_teaching_rows" :key="`nt-${i}`" class="row-nt">
                    <td class="text-center">{{ r.tl }}</td>
                    <td></td>
                    <td>{{ r.discipline }}</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>{{ r.text }}</td>
                    <td class="text-caption text-grey-7">{{ r.type }}</td>
                  </tr>
                  <tr v-for="(r, i) in mapaData.teaching_rows" :key="`t-${i}`">
                    <td class="text-center">{{ r.tl }}</td>
                    <td>{{ r.class_name }}</td>
                    <td>{{ r.discipline }}</td>
                    <td class="text-center">{{ r.turno }}</td>
                    <td class="text-center">{{ r.semestral ? 'Sem.' : '' }}</td>
                    <td>{{ r.room }}</td>
                    <td>{{ r.text }}</td>
                    <td>{{ r.description }}</td>
                  </tr>
                  <tr class="row-total">
                    <td class="text-center text-weight-bold">{{ mapaData.total_tl }}</td>
                    <td colspan="7" class="text-caption text-weight-bold">Total horas letivas semanais</td>
                  </tr>
                </tbody>
              </table>
            </q-card-section>
          </q-card>
        </template>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import { useAcademicYearsStore } from 'stores/academicYears'
import { useExport } from '../composables/useExport'

const $q = useQuasar()
const yearsStore = useAcademicYearsStore()
const { printHTML, downloadHTML } = useExport()

interface Teacher {
  id: number
  name: string
  primary_school_id: number | null
  primary_school_name: string | null
}

interface MapaData {
  teacher: { id: number; name: string; school_name?: string; cluster_name?: string }
  academic_year_name: string
  non_teaching_rows: { tl: number; discipline: string; text: string; type: string }[]
  teaching_rows: {
    tl: number; class_name: string; discipline: string; turno: string
    semestral: boolean; room: string; text: string; description: string
  }[]
  total_tl: number
}

const loading = ref(false)
const mapaLoading = ref(false)

const selectedYearId = ref<number | null>(null)
const selectedTimetableId = ref<number | null>(null)
const selectedSchoolId = ref<number | null>(null)
const selectedTeacherId = ref<number | null>(null)
const search = ref('')

const teachers = ref<Teacher[]>([])
const timetableOptions = ref<{ label: string; value: number }[]>([])
const availableSchools = ref<{ id: number; name: string }[]>([])
const mapaData = ref<MapaData | null>(null)

const yearOptions = computed(() =>
  yearsStore.years.map((y) => ({ label: y.name, value: y.id }))
)

const schoolOptions = computed(() =>
  availableSchools.value.map((s) => ({ label: s.name, value: s.id }))
)

const filteredTeachers = computed(() => {
  let list = teachers.value
  if (selectedSchoolId.value !== null) {
    list = list.filter((t) => t.primary_school_id === selectedSchoolId.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter((t) => t.name.toLowerCase().includes(q))
  }
  return list
})

async function loadTeachers() {
  if (!selectedYearId.value) return
  loading.value = true
  mapaData.value = null
  selectedTeacherId.value = null
  try {
    const params: Record<string, unknown> = { academic_year_id: selectedYearId.value }
    if (selectedTimetableId.value) params.timetable_id = selectedTimetableId.value
    const { data } = await api.get('/service-distribution', { params })
    teachers.value = data.teachers
    timetableOptions.value = (data.timetables as { id: number; name: string }[]).map(
      (t) => ({ label: t.name, value: t.id })
    )
    availableSchools.value = data.schools ?? []
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar docentes' })
  } finally {
    loading.value = false
  }
}

async function loadMapa() {
  if (!selectedTeacherId.value || !selectedYearId.value) return
  mapaLoading.value = true
  try {
    const params: Record<string, unknown> = { academic_year_id: selectedYearId.value }
    if (selectedTimetableId.value) params.timetable_id = selectedTimetableId.value
    const { data } = await api.get(
      `/service-distribution/mapa-servico/${selectedTeacherId.value}`,
      { params }
    )
    mapaData.value = data
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar mapa de serviço' })
    mapaData.value = null
  } finally {
    mapaLoading.value = false
  }
}

async function onYearChange() {
  selectedTimetableId.value = null
  timetableOptions.value = []
  teachers.value = []
  mapaData.value = null
  selectedTeacherId.value = null
  await loadTeachers()
}

async function onTimetableChange() {
  await loadTeachers()
  if (selectedTeacherId.value) await loadMapa()
}

function selectTeacher(t: Teacher) {
  selectedTeacherId.value = t.id
  void loadMapa()
}

// ── Export helpers ────────────────────────────────────────────────────────────

const mapaExtraStyles = `
  .header { display: flex; justify-content: space-between; margin-bottom: 16px; }
  .header-left h3 { font-size: 14px; margin: 0 0 2px; }
  .header-left p { margin: 2px 0; font-size: 11px; }
  .header-right { font-size: 14px; font-weight: bold; }
  table { border-collapse: collapse; width: 100%; font-size: 11px; }
  th, td { border: 1px solid #999; padding: 3px 6px; vertical-align: middle; }
  th { background: #2c3e50; color: #fff; font-size: 10px; font-weight: 600; }
  td.num { text-align: center; width: 32px; }
  tr:nth-child(even) td { background: #f5f5f5; }
  tr.nt td { background: #fffde7; }
  tr.total td { border-top: 2px solid #333; font-weight: bold; background: #f0f0f0; }
`

function buildMapaHtml(): string {
  if (!mapaData.value) return ''
  const { teacher, academic_year_name, non_teaching_rows, teaching_rows, total_tl } = mapaData.value
  const ntRows = non_teaching_rows
    .map(
      (r) => `<tr class="nt">
      <td class="num">${r.tl}</td><td></td><td>${r.discipline}</td>
      <td></td><td></td><td></td><td>${r.text}</td><td>${r.type}</td>
    </tr>`
    )
    .join('\n')
  const tRows = teaching_rows
    .map(
      (r) => `<tr>
      <td class="num">${r.tl}</td><td>${r.class_name}</td><td>${r.discipline}</td>
      <td style="text-align:center">${r.turno}</td>
      <td style="text-align:center">${r.semestral ? 'Sem.' : ''}</td>
      <td>${r.room}</td><td>${r.text}</td><td>${r.description}</td>
    </tr>`
    )
    .join('\n')
  return `
<div class="header">
  <div class="header-left">
    <h3>${teacher.cluster_name || teacher.school_name || ''}</h3>
    <p>${teacher.school_name || ''}</p>
    <p>Horários ${academic_year_name}</p>
  </div>
  <div class="header-right">${teacher.name}</div>
</div>
<table>
  <thead><tr>
    <th>TL</th><th>Turma/s</th><th>Disciplina</th>
    <th>Turnos</th><th>Semestral</th><th>Sala</th>
    <th>Texto</th><th>Descrição</th>
  </tr></thead>
  <tbody>
    ${ntRows}
    ${tRows}
    <tr class="total">
      <td class="num">${total_tl}</td>
      <td colspan="7">Total horas letivas semanais</td>
    </tr>
  </tbody>
</table>`
}

function printMapa() {
  if (!mapaData.value) return
  printHTML(`Mapa de Serviço — ${mapaData.value.teacher.name}`, buildMapaHtml(), mapaExtraStyles)
}

function downloadMapa() {
  if (!mapaData.value) return
  const slug = mapaData.value.teacher.name.replace(/\s+/g, '-').toLowerCase()
  downloadHTML(
    `Mapa de Serviço — ${mapaData.value.teacher.name}`,
    buildMapaHtml(),
    `mapa-servico-${slug}`,
    mapaExtraStyles
  )
}

onMounted(async () => {
  if (yearsStore.years.length === 0) await yearsStore.fetchAll()
  const active =
    yearsStore.years.find((y) => (y as unknown as { is_active: boolean }).is_active) ??
    yearsStore.years[0]
  if (active) {
    selectedYearId.value = active.id
    await loadTeachers()
  }
})
</script>

<style scoped>
.mapa-table {
  border-collapse: collapse;
  width: 100%;
  font-size: 12px;
}
.mapa-table th,
.mapa-table td {
  border: 1px solid #ddd;
  padding: 4px 8px;
  vertical-align: middle;
}
.mapa-table th {
  background: #2c3e50;
  color: white;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.mapa-table .row-nt td {
  background: #fffde7;
}
.mapa-table .row-total td {
  border-top: 2px solid #555;
  background: #f0f0f0;
  font-weight: bold;
}
</style>
