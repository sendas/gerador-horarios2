<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5 col">Disciplinas</div>
      <q-space />
      <q-input v-model="search" placeholder="Pesquisar..." dense outlined clearable style="min-width:200px">
        <template #prepend><q-icon name="search" /></template>
      </q-input>
      <ExportButton class="q-ml-sm" :sort-options="subjectSortOptions" @export="doExport" />
      <q-btn color="primary" icon="add" label="Nova" @click="openCreate" class="q-ml-sm" />
    </div>

    <q-table :rows="subjectsStore.subjects" :columns="columns" row-key="id" :loading="subjectsStore.loading" :filter="search" sort-by="name">
      <template #body-cell-color="{ row }">
        <q-td auto-width>
          <div style="width:22px;height:22px;border-radius:4px;display:inline-block" :style="{ background: row.color }" />
        </q-td>
      </template>
      <template #body-cell-weekly_structure="{ row }">
        <q-td>
          <span class="structure-badge">{{ structureLabel(row.weekly_structure) }}</span>
        </q-td>
      </template>
      <template #body-cell-regime="{ row }">
        <q-td>
          <q-badge :color="row.regime === 'semestral' ? 'orange-7' : 'teal-7'" :label="row.regime === 'semestral' ? 'Semestral' : 'Anual'" />
          <span v-if="row.paired_subject_name" class="text-caption text-grey-6 q-ml-xs">
            ↔ {{ row.paired_subject_name }}
          </span>
        </q-td>
      </template>
      <template #body-cell-flags="{ row }">
        <q-td>
          <q-badge v-if="row.is_physical_education" color="orange-7" label="EF" class="q-mr-xs" />
          <q-badge v-if="row.can_exempt_articulado" color="teal-7" label="Articulado" />
        </q-td>
      </template>
      <template #body-cell-actions="{ row }">
        <q-td auto-width>
          <q-btn unelevated size="sm" color="grey-6" icon="edit" label="Editar" @click="openEdit(row)" class="q-mr-xs" />
          <q-btn unelevated size="sm" color="negative" icon="delete" label="Apagar" @click="confirmDelete(row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Create / Edit dialog -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width:340px;max-width:560px;width:100%;max-height:92vh;display:flex;flex-direction:column">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">{{ editing ? 'Editar' : 'Nova' }} Disciplina</div>
        </q-card-section>
        <q-card-section class="q-gutter-sm" style="overflow-y:auto;flex:1">
          <q-form @submit="save">
            <q-select
              v-model="form.cluster_id" :options="clusterOptions"
              label="Agrupamento *" emit-value map-options dense
              :rules="[v => !!v || 'Obrigatório']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col">
                <q-input v-model="form.name" label="Nome *" dense :rules="[v => !!v || 'Obrigatório']" />
              </div>
              <div class="col-4">
                <q-input v-model="form.code" label="Código" dense />
              </div>
            </div>

            <!-- Colour picker -->
            <div class="q-mt-sm">
              <div class="text-caption text-grey-7 q-mb-xs">Cor</div>
              <div class="row q-gutter-xs">
                <div
                  v-for="c in colorPalette" :key="c"
                  :style="{
                    background: c, width: '28px', height: '28px', borderRadius: '4px',
                    cursor: 'pointer',
                    outline: form.color === c ? '3px solid #333' : '2px solid transparent',
                    outlineOffset: '1px',
                  }"
                  @click="form.color = c"
                />
              </div>
            </div>

            <q-separator class="q-my-md" />

            <!-- Weekly structure -->
            <div class="text-subtitle2 q-mb-sm">Funcionamento semanal</div>
            <div class="structure-grid q-mb-sm">
              <div
                v-for="opt in structureOptions" :key="opt.value"
                class="structure-option"
                :class="{ 'structure-option--active': form.weekly_structure === opt.value }"
                @click="form.weekly_structure = opt.value"
              >
                <div class="structure-visual">
                  <span v-for="(b, i) in opt.blocks" :key="i" class="structure-block" :class="b === 2 ? 'structure-block--double' : ''">
                    <span v-if="b === 2">■■</span>
                    <span v-else>■</span>
                  </span>
                </div>
                <div class="structure-label text-caption">{{ opt.label }}</div>
                <div class="structure-hint text-caption text-grey-6">{{ opt.hint }}</div>
              </div>
            </div>

            <!-- Regime -->
            <div class="text-subtitle2 q-mb-xs q-mt-md">Regime</div>
            <q-btn-toggle
              v-model="form.regime"
              :options="[
                { label: 'Anual', value: 'annual', icon: 'event_repeat' },
                { label: 'Semestral', value: 'semestral', icon: 'event' },
              ]"
              color="primary" outline dense
            />
            <div v-if="form.regime === 'semestral'" class="q-gutter-sm q-mt-sm">
              <q-select
                v-model="form.default_semester"
                :options="[{ label: '1.º Semestre', value: 1 }, { label: '2.º Semestre', value: 2 }]"
                label="Semestre padrão" emit-value map-options dense clearable
              />
              <q-select
                v-model="form.paired_subject_id"
                :options="pairedOptions"
                option-value="id"
                option-label="name"
                emit-value
                map-options
                dense
                clearable
                label="Disciplina par (ocupa o mesmo horário no semestre oposto)"
                hint="Ex: TIC no 1.º Sem ↔ EV no 2.º Sem — partilham os mesmos tempos no horário da turma"
              />
            </div>

            <q-separator class="q-my-md" />
            <div class="text-subtitle2 q-mb-xs q-mt-sm">Características especiais</div>
            <q-toggle v-model="form.is_physical_education" label="Educação Física" color="orange-7" />
            <div class="text-caption text-grey-6 q-ml-xl q-mb-xs">Sujeita à regra 'sem EF depois do almoço'</div>
            <q-toggle v-model="form.can_exempt_articulado" label="Pode ter dispensa (ensino articulado)" color="teal-7" />
            <div class="text-caption text-grey-6 q-ml-xl q-mb-sm">Alunos de ensino articulado podem ser dispensados desta disciplina</div>

            <q-select
              v-model="form.required_room_type"
              :options="roomTypeOptions"
              label="Tipo de sala obrigatório"
              dense clearable use-input new-value-mode="add-unique"
              input-debounce="0"
              class="q-mt-sm"
            >
              <template #prepend><q-icon name="meeting_room" color="brown-6" /></template>
            </q-select>
            <div class="text-caption text-grey-6 q-mb-xs">
              As aulas desta disciplina só usam salas deste tipo (ex: <em>gym</em> para EF, <em>lab</em> para CN/FQ).
              Deixa vazio para qualquer sala. Os tipos correspondem ao campo "Tipo" em <strong>Salas</strong>.
            </div>

            <div class="row justify-end q-mt-lg q-gutter-sm">
              <q-btn flat label="Cancelar" v-close-popup />
              <q-btn type="submit" color="primary" :label="editing ? 'Guardar' : 'Criar'" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import { useSubjectsStore, type Subject } from 'stores/subjects'
import { useClustersStore } from 'stores/clusters'
import ExportButton, { type SortOption } from 'components/ExportButton.vue'
import { useExport, type ExportColumn } from '../composables/useExport'

const $q = useQuasar()
const subjectsStore = useSubjectsStore()
const clustersStore = useClustersStore()
const { exportToPDF, exportToHTML, exportToCSV, sortRows } = useExport()

const colorPalette = [
  '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
  '#1abc9c', '#e67e22', '#34495e', '#e91e63', '#00bcd4',
  '#8bc34a', '#ff5722', '#607d8b', '#795548', '#ff9800',
]

const structureOptions = [
  { value: '1',       label: '1 tempo / semana',              hint: 'Uma aula isolada',                    blocks: [1] },
  { value: '1+1',     label: '2 tempos separados',             hint: 'Duas aulas em dias diferentes',       blocks: [1, 1] },
  { value: '1+1+1',   label: '3 tempos separados',             hint: 'Três aulas em dias diferentes',       blocks: [1, 1, 1] },
  { value: '1+1+1+1', label: '4 tempos separados',             hint: 'Quatro aulas em dias diferentes',     blocks: [1, 1, 1, 1] },
  { value: '2',       label: 'Bloco duplo',                    hint: '2 aulas consecutivas',                blocks: [2] },
  { value: '2+1',     label: 'Bloco duplo + 1 separado',       hint: 'O mais comum (3 tempos)',             blocks: [2, 1] },
  { value: '2+1+1',   label: 'Bloco duplo + 2 separados',      hint: '4 tempos: 1 bloco + 2 isolados',      blocks: [2, 1, 1] },
  { value: '2+2',     label: 'Dois blocos duplos',             hint: '4 tempos em 2 blocos',                blocks: [2, 2] },
  { value: '2+2+1',   label: 'Dois blocos duplos + 1 separado',hint: '5 tempos: 2 blocos + 1 isolado',      blocks: [2, 2, 1] },
  { value: '3',       label: 'Bloco triplo',                   hint: '3 aulas consecutivas',                blocks: [3] },
  { value: '3+1',     label: 'Bloco triplo + 1 separado',      hint: '4 tempos: 1 bloco de 3 + 1 isolado',  blocks: [3, 1] },
  { value: '3+2',     label: 'Bloco triplo + bloco duplo',     hint: '5 tempos: 1 bloco de 3 + 1 de 2',    blocks: [3, 2] },
]

function structureLabel(v: string) {
  return structureOptions.find((o) => o.value === v)?.label ?? v
}

const columns = [
  { name: 'name', label: 'Nome', field: 'name', align: 'left' as const, sortable: true },
  { name: 'code', label: 'Código', field: 'code', align: 'left' as const },
  { name: 'color', label: 'Cor', field: 'color', align: 'center' as const },
  { name: 'weekly_structure', label: 'Funcionamento', field: 'weekly_structure', align: 'left' as const },
  { name: 'regime', label: 'Regime', field: 'regime', align: 'center' as const },
  { name: 'flags', label: 'Flags', field: 'id', align: 'left' as const },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' as const },
]

const exportColumns: ExportColumn[] = [
  { label: 'Nome', field: 'name' },
  { label: 'Código', field: 'code' },
  { label: 'Funcionamento', field: (r) => structureLabel(r.weekly_structure as string) },
  { label: 'Regime', field: (r) => r.regime === 'semestral' ? 'Semestral' : 'Anual', align: 'center' },
  { label: 'Ed. Física', field: (r) => r.is_physical_education ? 'Sim' : 'Não', align: 'center' },
  { label: 'Articulado', field: (r) => r.can_exempt_articulado ? 'Sim' : 'Não', align: 'center' },
]

const subjectSortOptions: SortOption[] = [
  { label: 'Nome', field: 'name' },
  { label: 'Código', field: (r) => String(r.code ?? '') },
]

function doExport({ format, sortBy, sortDir }: { format: 'pdf' | 'html' | 'csv' | 'excel'; sortBy: SortOption | null; sortDir: 'asc' | 'desc' }) {
  const rows = sortRows(subjectsStore.subjects as unknown as Record<string, unknown>[], sortBy, sortDir)
  if (format === 'pdf') exportToPDF('Disciplinas', rows, exportColumns)
  else if (format === 'html') exportToHTML('Disciplinas', rows, exportColumns, 'disciplinas')
  else exportToCSV(rows, exportColumns, 'disciplinas')
}

const search = ref('')
const dialog = ref(false)
const editing = ref<Subject | null>(null)
const form = ref({
  cluster_id: null as number | null,
  name: '', code: '', color: '#3498db',
  weekly_structure: '1+1',
  regime: 'annual',
  default_semester: null as number | null,
  paired_subject_id: null as number | null,
  is_physical_education: false,
  can_exempt_articulado: false,
  required_room_type: null as string | null,
})

// Room types already registered in /rooms — offered as suggestions
const roomTypeOptions = ref<string[]>([])
async function loadRoomTypes() {
  try {
    const { data } = await api.get<{ room_type?: string }[]>('/rooms')
    roomTypeOptions.value = [...new Set(data.map(r => r.room_type).filter((t): t is string => !!t))].sort()
  } catch { /* rooms endpoint unavailable — free text still works */ }
}

const clusterOptions = computed(() => clustersStore.clusters.map((c) => ({ label: c.name, value: c.id })))

// subjects in same cluster that are semestral and not the current one
const pairedOptions = computed(() =>
  subjectsStore.subjects.filter((s) =>
    s.cluster_id === form.value.cluster_id &&
    s.regime === 'semestral' &&
    s.id !== editing.value?.id
  )
)

// Clear paired when switching to annual
watch(() => form.value.regime, (val) => {
  if (val !== 'semestral') {
    form.value.paired_subject_id = null
    form.value.default_semester = null
  }
})

onMounted(async () => {
  await Promise.all([subjectsStore.fetchAll(), clustersStore.fetchAll(), loadRoomTypes()])
})

function openCreate() {
  editing.value = null
  form.value = { cluster_id: null, name: '', code: '', color: '#3498db', weekly_structure: '1+1', regime: 'annual', default_semester: null, paired_subject_id: null, is_physical_education: false, can_exempt_articulado: false, required_room_type: null }
  dialog.value = true
}

function openEdit(row: Subject) {
  editing.value = row
  form.value = {
    cluster_id: row.cluster_id, name: row.name, code: row.code || '',
    color: row.color, weekly_structure: row.weekly_structure || '1+1',
    regime: row.regime || 'annual', default_semester: row.default_semester ?? null,
    paired_subject_id: row.paired_subject_id ?? null,
    is_physical_education: row.is_physical_education || false,
    can_exempt_articulado: row.can_exempt_articulado || false,
    required_room_type: row.required_room_type ?? null,
  }
  dialog.value = true
}

async function save() {
  if (!form.value.cluster_id) return
  try {
    if (editing.value) {
      await subjectsStore.update(editing.value.id, form.value)
      $q.notify({ type: 'positive', message: 'Disciplina atualizada' })
    } else {
      await subjectsStore.create(form.value as Omit<Subject, 'id'>)
      $q.notify({ type: 'positive', message: 'Disciplina criada' })
    }
    dialog.value = false
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao guardar' })
  }
}

function confirmDelete(row: Subject) {
  $q.dialog({
    title: 'Confirmar eliminação',
    message: `Eliminar "${row.name}"?`,
    ok: { label: 'Eliminar', color: 'negative' },
    cancel: true,
  }).onOk(async () => {
    await subjectsStore.remove(row.id)
    $q.notify({ type: 'positive', message: 'Eliminada' })
  })
}
</script>

<style scoped>
.structure-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
@media (max-width: 480px) {
  .structure-grid { grid-template-columns: repeat(2, 1fr); }
}

.structure-option {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 8px 6px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.structure-option:hover { border-color: #90caf9; background: #f5f5f5; }
.structure-option--active { border-color: #1976d2; background: #e3f2fd; }
.body--dark .structure-option:hover { background: rgba(255,255,255,0.08); }
.body--dark .structure-option--active { background: rgba(25,118,210,0.25); border-color: #64b5f6; }

.structure-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3px;
  margin-bottom: 4px;
  min-height: 22px;
  font-size: 14px;
}
.structure-block { color: #1976d2; font-weight: bold; letter-spacing: -1px; }
.structure-block--double { color: #e53935; }

.structure-label { font-weight: 600; font-size: 11px; line-height: 1.2; }
.structure-hint { font-size: 10px; margin-top: 2px; }

.structure-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e3f2fd;
  color: #1565c0;
}
.body--dark .structure-badge { background: rgba(25,118,210,0.2); color: #90caf9; }
</style>
