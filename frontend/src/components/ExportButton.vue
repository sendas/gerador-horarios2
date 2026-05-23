<template>
  <q-btn-dropdown
    flat
    dense
    size="sm"
    color="grey-7"
    icon="download"
    :label="label"
    :title="title"
    :disable="disable"
  >
    <q-list dense style="min-width: 160px">
      <q-item-label header class="text-caption text-grey-6 q-py-xs">Exportar como…</q-item-label>

      <q-item clickable v-close-popup @click="$emit('export', 'pdf')">
        <q-item-section avatar style="min-width: 32px">
          <q-icon name="picture_as_pdf" color="red-7" size="sm" />
        </q-item-section>
        <q-item-section>PDF <span class="text-caption text-grey-6">(imprimir)</span></q-item-section>
      </q-item>

      <q-item clickable v-close-popup @click="$emit('export', 'html')">
        <q-item-section avatar style="min-width: 32px">
          <q-icon name="code" color="orange-7" size="sm" />
        </q-item-section>
        <q-item-section>HTML</q-item-section>
      </q-item>

      <q-item v-if="csv" clickable v-close-popup @click="$emit('export', 'csv')">
        <q-item-section avatar style="min-width: 32px">
          <q-icon name="table_chart" color="green-7" size="sm" />
        </q-item-section>
        <q-item-section>CSV</q-item-section>
      </q-item>

      <q-item v-if="excel" clickable v-close-popup @click="$emit('export', 'excel')">
        <q-item-section avatar style="min-width: 32px">
          <q-icon name="grid_on" color="teal-7" size="sm" />
        </q-item-section>
        <q-item-section>Excel (CSV)</q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  label?: string
  title?: string
  csv?: boolean
  excel?: boolean
  disable?: boolean
}>(), {
  label: 'Exportar',
  title: 'Exportar tabela',
  csv: true,
  excel: false,
  disable: false,
})

defineEmits<{
  (e: 'export', format: 'pdf' | 'html' | 'csv' | 'excel'): void
}>()
</script>
