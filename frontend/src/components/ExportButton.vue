<template>
  <q-btn-dropdown
    flat dense size="sm" color="grey-7" icon="download"
    :label="label" :title="title" :disable="disable"
  >
    <q-list dense style="min-width: 160px">
      <q-item-label header class="text-caption text-grey-6 q-py-xs">Exportar como…</q-item-label>
      <q-item clickable v-close-popup @click="select('pdf')">
        <q-item-section avatar style="min-width:32px"><q-icon name="picture_as_pdf" color="red-7" size="sm" /></q-item-section>
        <q-item-section>PDF <span class="text-caption text-grey-6">(imprimir)</span></q-item-section>
      </q-item>
      <q-item clickable v-close-popup @click="select('html')">
        <q-item-section avatar style="min-width:32px"><q-icon name="code" color="orange-7" size="sm" /></q-item-section>
        <q-item-section>HTML</q-item-section>
      </q-item>
      <q-item v-if="csv" clickable v-close-popup @click="select('csv')">
        <q-item-section avatar style="min-width:32px"><q-icon name="table_chart" color="green-7" size="sm" /></q-item-section>
        <q-item-section>CSV</q-item-section>
      </q-item>
      <q-item v-if="excel" clickable v-close-popup @click="select('excel')">
        <q-item-section avatar style="min-width:32px"><q-icon name="grid_on" color="teal-7" size="sm" /></q-item-section>
        <q-item-section>Excel (CSV)</q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>

  <!-- Sort/filter dialog -->
  <q-dialog v-model="showDialog" persistent>
    <q-card style="min-width:320px">
      <q-card-section class="bg-primary text-white q-py-sm">
        <div class="text-subtitle2">Opções de exportação</div>
      </q-card-section>
      <q-card-section class="q-gutter-sm">
        <q-select
          v-model="sortBy"
          :options="sortOptions"
          option-label="label"
          label="Ordenar por"
          clearable dense outlined emit-value map-options
        />
        <div class="row q-gutter-sm">
          <q-btn-toggle
            v-model="sortDir"
            dense unelevated
            :options="[{label:'↑ Ascendente', value:'asc'}, {label:'↓ Descendente', value:'desc'}]"
            color="primary" text-color="white" toggle-color="primary"
          />
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancelar" @click="showDialog = false" />
        <q-btn color="primary" label="Exportar" icon="download" @click="confirmExport" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export interface SortOption {
  label: string
  field: string | ((row: Record<string, unknown>) => string)
}

const props = withDefaults(defineProps<{
  label?: string
  title?: string
  csv?: boolean
  excel?: boolean
  disable?: boolean
  sortOptions?: SortOption[]
}>(), {
  label: 'Exportar',
  title: 'Exportar tabela',
  csv: true,
  excel: false,
  disable: false,
  sortOptions: () => [],
})

const emit = defineEmits<{
  (e: 'export', payload: { format: 'pdf' | 'html' | 'csv' | 'excel'; sortBy: SortOption | null; sortDir: 'asc' | 'desc' }): void
}>()

const showDialog = ref(false)
const pendingFormat = ref<'pdf' | 'html' | 'csv' | 'excel'>('pdf')
const sortBy = ref<SortOption | null>(props.sortOptions?.[0] ?? null)
const sortDir = ref<'asc' | 'desc'>('asc')

function select(format: 'pdf' | 'html' | 'csv' | 'excel') {
  pendingFormat.value = format
  if (props.sortOptions?.length) {
    showDialog.value = true
  } else {
    emit('export', { format, sortBy: null, sortDir: 'asc' })
  }
}

function confirmExport() {
  emit('export', { format: pendingFormat.value, sortBy: sortBy.value, sortDir: sortDir.value })
  showDialog.value = false
}
</script>
