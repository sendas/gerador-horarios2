<template>
  <div :class="`pt-card pt-theme-${theme}`">
    <!-- Header row -->
    <div class="pt-row pt-head">
      <div>Nome</div>
      <div class="pt-col-base">Escola base</div>
      <div>Disciplinas</div>
      <div class="pt-num">CL líq.</div>
      <div class="pt-num">Máx/dia</div>
      <div class="pt-col-free">Dia livre</div>
      <div class="pt-right">Ações</div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="pt-loading">A carregar…</div>

    <!-- Data rows -->
    <template v-else v-for="(row, i) in rows" :key="row.id ?? i">
      <div class="pt-row" :class="{ 'pt-row--expanded': expandedIdx === i }">

        <!-- Name + chevron -->
        <div class="pt-name-cell">
          <button
            class="pt-caret-btn"
            :class="{ 'is-open': expandedIdx === i }"
            :aria-label="expandedIdx === i ? 'Recolher' : 'Expandir'"
            @click="toggleExpand(i, row)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          <span class="pt-name" :title="row.name">{{ row.name }}</span>
        </div>

        <!-- Escola base -->
        <div class="pt-col-base">
          <span v-if="row.baseWarn" class="pt-warn-text">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <circle cx="12" cy="17" r=".5" fill="currentColor"/>
            </svg>
            <span>sem escola</span>
          </span>
          <span v-else class="pt-muted-2">{{ row.base }}</span>
        </div>

        <!-- Disciplinas (pills) -->
        <div class="pt-col-subjects">
          <div class="pt-subjects">
            <span v-for="(s, si) in (row.subjects ?? [])" :key="si" class="pt-pill">{{ s }}</span>
            <span v-if="!row.subjects?.length" class="pt-muted">—</span>
          </div>
        </div>

        <!-- Métricas -->
        <div class="pt-num pt-col-cl">{{ row.cl ?? '—' }}</div>
        <div class="pt-num pt-col-max">{{ row.max ?? '—' }}</div>
        <div class="pt-col-free">{{ row.free || '—' }}</div>

        <!-- Ações -->
        <div class="pt-actions">
          <button class="pt-btn-edit" @click="emit('editar', row)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4z"/>
            </svg>
            <span>Editar</span>
          </button>

          <div class="pt-menu-wrap">
            <button
              class="pt-btn-more"
              aria-label="Mais ações"
              aria-haspopup="menu"
              :aria-expanded="String(openMenuIdx === i)"
              @click.stop="toggleMenu(i)"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="5" r="1.5"/>
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="12" cy="19" r="1.5"/>
              </svg>
              <span>Mais</span>
            </button>

            <div v-if="openMenuIdx === i" class="pt-menu" role="menu" @click.stop>
              <button @click="fire('escolas', row)">
                <span class="pt-mi pt-mi-cy">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
                  </svg>
                </span>
                Escolas
              </button>
              <button @click="fire('disciplinas', row)">
                <span class="pt-mi pt-mi-tl">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                  </svg>
                </span>
                Disciplinas
              </button>
              <button @click="fire('turmas', row)">
                <span class="pt-mi pt-mi-tl2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </span>
                Turmas
              </button>
              <button @click="fire('disponibilidade', row)">
                <span class="pt-mi pt-mi-gr">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
                  </svg>
                </span>
                Disponibilidade
              </button>
              <div class="pt-menu-sep"/>
              <button class="pt-danger" @click="fire('apagar', row)">
                <span class="pt-mi pt-mi-rd">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                    <path d="M10 11v6M14 11v6M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>
                  </svg>
                </span>
                Apagar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Painel expandido (slot) -->
      <div v-if="expandedIdx === i" class="pt-detail-wrap">
        <slot name="detail" :row="row" :idx="i" />
      </div>
    </template>
  </div>
</template>

<script lang="ts">
export interface PtRow {
  id?: string | number
  name: string
  base: string
  baseWarn?: boolean
  subjects?: string[]
  cl?: number | string | null
  max?: number | string | null
  free?: string | null
}
</script>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { PtRow } from './ProfessoresTable.vue'

withDefaults(defineProps<{
  rows?: PtRow[]
  theme?: 'dark' | 'light'
  loading?: boolean
}>(), {
  rows: () => [],
  theme: 'light',
  loading: false,
})

const emit = defineEmits<{
  (e: 'editar', row: PtRow): void
  (e: 'escolas', row: PtRow): void
  (e: 'disciplinas', row: PtRow): void
  (e: 'turmas', row: PtRow): void
  (e: 'disponibilidade', row: PtRow): void
  (e: 'apagar', row: PtRow): void
  (e: 'expand', row: PtRow | null): void
}>()

const openMenuIdx = ref<number | null>(null)
const expandedIdx = ref<number | null>(null)

function toggleMenu(i: number) {
  openMenuIdx.value = openMenuIdx.value === i ? null : i
}

function closeMenu() {
  openMenuIdx.value = null
}

function fire(event: 'escolas' | 'disciplinas' | 'turmas' | 'disponibilidade' | 'apagar', row: PtRow) {
  closeMenu()
  emit(event, row)
}

function toggleExpand(i: number, row: PtRow) {
  if (expandedIdx.value === i) {
    expandedIdx.value = null
    emit('expand', null)
  } else {
    expandedIdx.value = i
    emit('expand', row)
  }
}

function onDocClick() { closeMenu() }
function onDocKey(e: KeyboardEvent) { if (e.key === 'Escape') closeMenu() }

onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onDocKey)
})
onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onDocKey)
})
</script>
