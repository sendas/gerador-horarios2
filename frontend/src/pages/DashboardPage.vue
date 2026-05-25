<template>
  <q-page class="dashboard-root">
    <!-- Hero with animated gradient + soft grain -->
    <section class="dash-hero">
      <div class="dash-hero__bg"></div>
      <div class="dash-hero__grain"></div>
      <div class="dash-hero__inner">
        <div class="dash-hero__brand">
          <q-icon name="hub" size="44px" class="dash-hero__brand-icon" />
          <span class="dash-hero__brand-name">Sinaptik2</span>
        </div>
        <h1 class="dash-hero__title">
          Horários escolares,<br />
          <span class="dash-hero__title-accent">gerados em segundos.</span>
        </h1>
        <p class="dash-hero__sub">
          Plataforma inteligente para agrupamentos — geração automática por OR-Tools,
          sem conflitos, com restrições configuráveis.
        </p>
        <div class="dash-hero__cta">
          <q-btn
            unelevated rounded
            color="white" text-color="primary"
            label="Ir para horários"
            icon-right="arrow_forward"
            class="dash-hero__btn-primary"
            data-testid="dash-cta-timetables"
            @click="router.push('/timetables')"
          />
          <q-btn
            flat rounded
            color="white"
            label="Configurar regras"
            icon="rule"
            class="dash-hero__btn-secondary"
            data-testid="dash-cta-rules"
            @click="router.push('/scheduling-rules')"
          />
        </div>
      </div>
    </section>

    <!-- Stats grid -->
    <section class="dash-section">
      <div class="dash-section__head">
        <span class="dash-section__eyebrow">Resumo</span>
        <h2 class="dash-section__title">Estado actual do agrupamento</h2>
      </div>

      <div class="row q-col-gutter-md">
        <div
          class="col-6 col-sm-3"
          v-for="(stat, i) in stats"
          :key="stat.label"
        >
          <q-card
            flat bordered
            class="stat-card"
            :style="{ animationDelay: `${i * 80}ms` }"
            :data-testid="`stat-card-${stat.label.toLowerCase()}`"
          >
            <div class="stat-card__accent" :style="{ background: stat.gradient }"></div>
            <q-card-section class="stat-card__body">
              <div class="stat-card__top">
                <span class="stat-card__label">{{ stat.label }}</span>
                <q-icon :name="stat.icon" size="22px" :style="{ color: stat.accent }" />
              </div>
              <div class="stat-card__value">
                {{ stat.display }}
              </div>
              <div class="stat-card__sub">
                <q-icon name="trending_flat" size="14px" />
                <span>registos activos</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Quick links -->
    <section class="dash-section">
      <div class="dash-section__head">
        <span class="dash-section__eyebrow">Acesso rápido</span>
        <h2 class="dash-section__title">Saltar para…</h2>
      </div>

      <div class="row q-col-gutter-md">
        <div
          class="col-6 col-sm-4 col-md-3"
          v-for="(link, i) in quickLinks"
          :key="link.to"
        >
          <q-card
            flat bordered
            class="link-card"
            clickable v-ripple
            :style="{ animationDelay: `${100 + i * 60}ms` }"
            :data-testid="`quick-link-${link.label.toLowerCase().replace(/\s+/g, '-')}`"
            @click="router.push(link.to)"
          >
            <q-card-section class="link-card__body">
              <div class="link-card__icon-wrap" :style="{ background: link.bg }">
                <q-icon :name="link.icon" size="22px" :style="{ color: link.color }" />
              </div>
              <div class="link-card__text">
                <div class="link-card__label">{{ link.label }}</div>
                <div class="link-card__hint">{{ link.hint }}</div>
              </div>
              <q-icon name="chevron_right" size="20px" class="link-card__chev" />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Guias Práticos -->
    <section class="dash-section dash-section--guides">
      <div class="dash-section__head">
        <span class="dash-section__eyebrow">Documentação</span>
        <h2 class="dash-section__title">Guias práticos</h2>
        <p class="dash-section__desc">
          Passo a passo para as configurações mais comuns.
        </p>
      </div>

      <div class="row q-col-gutter-md">
        <div
          v-for="(guide, gi) in guides"
          :key="guide.id"
          class="col-12 col-md-6"
        >
          <q-card
            flat bordered
            class="guide-card"
            :style="{ animationDelay: `${gi * 80}ms` }"
          >
            <q-expansion-item
              v-model="guide.open"
              :header-class="guide.open ? 'guide-card__header--open' : ''"
            >
              <template #header>
                <div class="guide-card__header-inner">
                  <div class="guide-card__icon-wrap" :style="{ background: guide.iconBg }">
                    <q-icon :name="guide.icon" size="20px" :style="{ color: guide.iconColor }" />
                  </div>
                  <div class="guide-card__meta">
                    <div class="guide-card__title">{{ guide.title }}</div>
                    <div class="guide-card__hint">{{ guide.hint }}</div>
                  </div>
                </div>
              </template>

              <q-separator />
              <q-card-section class="guide-card__body">
                <ol class="guide-steps">
                  <li
                    v-for="(step, si) in guide.steps"
                    :key="si"
                    class="guide-step"
                  >
                    <div class="guide-step__title">{{ step.title }}</div>
                    <div class="guide-step__desc" v-html="step.desc"></div>
                    <q-banner
                      v-if="step.note"
                      dense rounded
                      class="guide-step__note q-mt-xs"
                    >
                      <template #avatar><q-icon name="info" color="info" /></template>
                      <span v-html="step.note"></span>
                    </q-banner>
                  </li>
                </ol>
              </q-card-section>
            </q-expansion-item>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="dash-footer">
      © {{ new Date().getFullYear() }} Sinaptik2 —
      <q-icon name="auto_awesome" size="xs" class="q-mr-xs" />
      Horários inteligentes ·
      <a href="https://github.com/sendas/gerador-horarios" target="_blank" class="dash-footer__link">GitHub</a>
    </footer>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const router = useRouter()

type StatRow = {
  label: string
  value: number
  display: string
  icon: string
  accent: string
  gradient: string
}

const stats = ref<StatRow[]>([
  { label: 'Professores', value: 0, display: '0', icon: 'person',      accent: '#ea580c', gradient: 'linear-gradient(135deg,#ea580c,#f97316)' },
  { label: 'Turmas',      value: 0, display: '0', icon: 'group',       accent: '#1d4ed8', gradient: 'linear-gradient(135deg,#1e3a8a,#3b82f6)' },
  { label: 'Escolas',     value: 0, display: '0', icon: 'school',      accent: '#0d9488', gradient: 'linear-gradient(135deg,#0f766e,#14b8a6)' },
  { label: 'Horários',    value: 0, display: '0', icon: 'table_chart', accent: '#15803d', gradient: 'linear-gradient(135deg,#166534,#22c55e)' },
])

const quickLinks = computed(() => [
  { to: '/timetables',       icon: 'table_chart',  label: 'Horários',       hint: 'Ver e gerar',     color: '#15803d', bg: 'rgba(34,197,94,.10)' },
  { to: '/teachers',         icon: 'person',       label: 'Professores',    hint: 'Gestão do corpo docente', color: '#ea580c', bg: 'rgba(249,115,22,.10)' },
  { to: '/classes',          icon: 'group',        label: 'Turmas',         hint: 'Lista por ano e escola', color: '#1d4ed8', bg: 'rgba(59,130,246,.10)' },
  { to: '/subjects',         icon: 'book',         label: 'Disciplinas',    hint: 'Disciplinas e regimes', color: '#7c3aed', bg: 'rgba(124,58,237,.10)' },
  { to: '/schools',          icon: 'school',       label: 'Escolas',        hint: 'Escolas do agrupamento', color: '#0d9488', bg: 'rgba(20,184,166,.10)' },
  { to: '/scheduling-rules', icon: 'rule',         label: 'Regras',         hint: 'Restrições e prefs', color: '#dc2626', bg: 'rgba(239,68,68,.10)' },
  { to: '/curriculum-plans', icon: 'menu_book',    label: 'Currículo',      hint: 'Planos curriculares', color: '#7c3aed', bg: 'rgba(124,58,237,.10)' },
  { to: '/teacher-assignment', icon: 'assignment_ind', label: 'Atribuições', hint: 'Professor → turma', color: '#0d9488', bg: 'rgba(20,184,166,.10)' },
])

// ── Guides ────────────────────────────────────────────────────────────────────

type GuideStep = { title: string; desc: string; note?: string }
type Guide = { id: string; title: string; hint: string; icon: string; iconBg: string; iconColor: string; open: boolean; steps: GuideStep[] }

const guides = ref<Guide[]>([
  {
    id: 'semestral-oc',
    title: 'Disciplinas semestrais e Oferta Complementar (OC)',
    hint: 'Como configurar pares TIC + OC, Cidadania + OC e outros',
    icon: 'schema',
    iconBg: 'rgba(99,102,241,0.10)',
    iconColor: '#6366f1',
    open: false,
    steps: [
      {
        title: '1. Criar as disciplinas',
        desc: 'Aceda a <strong>Disciplinas</strong> e certifique-se de que existem entradas para:<br>'
          + '&bull; <strong>TIC</strong> — regime <em>Semestral</em>, estrutura semanal "1" (1 tempo por semana)<br>'
          + '&bull; <strong>OC-TIC</strong> (Oferta Complementar de TIC) — regime <em>Semestral</em>, estrutura "1"<br>'
          + '&bull; <strong>CD</strong> (Cidadania) — regime <em>Anual</em>, estrutura "1" — toda a turma, todo o ano<br>'
          + '&bull; <strong>OC-CD</strong> (Oferta Complementar de CD) — regime <em>Anual</em>, estrutura "1" — crédito de 1h, também anual e para toda a turma',
        note: 'TIC + OC-TIC = 2 tempos semestrais (bloco TIC). CD + OC-CD = 2 tempos anuais (Cidadania tem 1h curricular + 1h de crédito OC). CD e OC-CD não são semestrais nem têm "par".',
      },
      {
        title: '2. Configurar o plano curricular',
        desc: 'Em <strong>Planos Curriculares</strong>, cria as seguintes entradas:<br>'
          + '<em>Bloco TIC (semestral, com par obrigatório):</em><br>'
          + '&bull; <strong>TIC</strong> — Semestral, 1.º sem, 1h, par: <em>disciplina do 2.º sem</em> (ex: ET, EV ou outra)<br>'
          + '&bull; <strong>OC-TIC</strong> — Semestral, 1.º sem, 1h, par: <em>OC da disciplina do 2.º sem</em><br>'
          + '&bull; A disciplina do 2.º sem — Semestral, 2.º sem, 1h, par: <em>TIC</em><br>'
          + '&bull; A OC da disciplina do 2.º sem — Semestral, 2.º sem, 1h, par: <em>OC-TIC</em><br>'
          + '<em>Bloco CD (anual, sem par):</em><br>'
          + '&bull; <strong>CD</strong> — <strong>Anual</strong>, 1h — <u>sem</u> checkbox "Semestral", <u>sem</u> par<br>'
          + '&bull; <strong>OC-CD</strong> — <strong>Anual</strong>, 1h — <u>sem</u> checkbox "Semestral", <u>sem</u> par',
        note: 'TIC é semestral e precisa sempre de uma disciplina par no 2.º semestre (não é CD — CD é anual). CD e OC-CD não têm par nem checkbox semestral.',
      },
      {
        title: '3. Configurar Turnos por turma (bloco TIC)',
        desc: 'Em <strong>Turmas</strong>, para cada turma cria dois turnos (T1 e T2) <em>apenas para o bloco TIC</em>:<br>'
          + '&bull; <strong>T1</strong>: alunos que fazem TIC+OC-TIC no 1.º semestre<br>'
          + '&bull; <strong>T2</strong>: alunos que fazem TIC+OC-TIC no 2.º semestre<br>'
          + 'CD e OC-CD são para <em>toda a turma</em> — não precisam de turnos.',
      },
      {
        title: '4. Aplicar o plano às turmas',
        desc: 'Ainda em Planos Curriculares, clique <strong>Aplicar às turmas</strong>. O sistema cria as 4 entradas curriculares em cada turma, com a relação semestral já definida.',
        note: 'Entradas existentes não são sobrepostas por omissão. Podes forçar a substituição na janela de aplicação.',
      },
      {
        title: '5. Atribuir professores',
        desc: 'Em <strong>Atribuição de Professores</strong>, atribui o professor de TIC às entradas TIC e OC-TIC (por turno T1/T2). '
          + 'Atribui o professor de CD às entradas CD e OC-CD — <em>sem turno</em>, pois são para toda a turma.',
      },
      {
        title: '6. Resultado no horário',
        desc: 'CD e OC-CD aparecem <em>todas as semanas</em>, todo o ano, para todos os alunos.<br>'
          + 'No bloco TIC, T1 tem TIC+OC-TIC no 1.º semestre e T2 tem TIC+OC-TIC no 2.º semestre.<br>'
          + 'No <strong>Mapa de Serviço Docente</strong>, cada entrada aparece numa linha separada com o turno e semestre.',
      },
    ],
  },
  {
    id: 'semestral-simples',
    title: 'Par semestral simples (ex: EV ↔ ET)',
    hint: 'Dois grupos de alunos fazem disciplinas diferentes em semestres alternados',
    icon: 'swap_horiz',
    iconBg: 'rgba(20,184,166,0.10)',
    iconColor: '#14b8a6',
    open: false,
    steps: [
      {
        title: '1. Criar as disciplinas',
        desc: 'Aceda a <strong>Disciplinas</strong> e certifique-se de que existem as duas disciplinas do par, ambas com regime <em>Semestral</em>.<br>'
          + 'Ex: <strong>EV</strong> (Educação Visual) e <strong>ET</strong> (Educação Tecnológica), cada uma com a estrutura semanal adequada.',
      },
      {
        title: '2. Configurar o plano curricular',
        desc: 'Em <strong>Planos Curriculares</strong>, cria duas entradas semestrais:<br>'
          + '&bull; <strong>EV</strong> — Semestral, 1.º sem, par: <em>ET</em><br>'
          + '&bull; <strong>ET</strong> — Semestral, 2.º sem, par: <em>EV</em><br>'
          + 'O "par" coloca ET nos <em>mesmos slots</em> de EV, mas no semestre oposto.',
        note: 'Os alunos têm EV no 1.º semestre e ET no 2.º semestre — sem divisão de grupos, a turma está sempre junta.',
      },
      {
        title: '3. Aplicar e atribuir professores',
        desc: 'Clique <strong>Aplicar às turmas</strong>. Depois, em <strong>Atribuição de Professores</strong>, atribui o professor de EV e o professor de ET às respetivas entradas. '
          + 'Cada professor leciona apenas no seu semestre.',
      },
    ],
  },
])

// Animated counter — increments from 0 to target over ~500ms
function animateTo(idx: number, target: number) {
  const start = performance.now()
  const dur = 500
  const initial = stats.value[idx].value
  const tick = (now: number) => {
    const p = Math.min(1, (now - start) / dur)
    const eased = 1 - Math.pow(1 - p, 3)
    const cur = Math.round(initial + (target - initial) * eased)
    stats.value[idx].value = cur
    stats.value[idx].display = cur.toString()
    if (p < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

onMounted(async () => {
  try {
    const [teachers, classes, schools, timetables] = await Promise.all([
      api.get('/teachers').then(r => r.data.length),
      api.get('/classes').then(r => r.data.length),
      api.get('/schools').then(r => r.data.length),
      api.get('/timetables').then(r => r.data.length),
    ])
    animateTo(0, teachers)
    animateTo(1, classes)
    animateTo(2, schools)
    animateTo(3, timetables)
  } catch {
    /* backend may not be reachable yet */
  }
})
</script>

<style scoped>
.dashboard-root {
  background: var(--dash-bg, #f7f8fb);
  min-height: 100vh;
}

/* ── HERO ──────────────────────────────────────────────────────────── */
.dash-hero {
  position: relative;
  overflow: hidden;
  padding: 64px 28px 72px;
  color: #fff;
  isolation: isolate;
}
.dash-hero__bg {
  position: absolute; inset: 0; z-index: -2;
  background:
    radial-gradient(60% 80% at 20% 0%, #6366f1 0%, transparent 60%),
    radial-gradient(50% 70% at 100% 30%, #0ea5e9 0%, transparent 60%),
    linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0c4a6e 100%);
  animation: hero-pan 22s ease-in-out infinite alternate;
}
.dash-hero__grain {
  position: absolute; inset: 0; z-index: -1;
  background-image:
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.06 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  opacity: 0.5;
  mix-blend-mode: overlay;
}
.dash-hero__inner {
  max-width: 920px;
  margin: 0 auto;
}
.dash-hero__brand {
  display: inline-flex; align-items: center; gap: 10px;
  margin-bottom: 22px;
  padding: 6px 14px 6px 8px;
  background: rgba(255,255,255,0.10);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
}
.dash-hero__brand-icon { opacity: 0.95; }
.dash-hero__brand-name { font-weight: 700; letter-spacing: 0.2px; font-size: 0.95rem; }
.dash-hero__title {
  font-size: clamp(2rem, 4.5vw, 3.4rem);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -1.2px;
  margin: 0 0 18px 0;
  animation: fade-up 0.7s ease-out both;
}
.dash-hero__title-accent {
  background: linear-gradient(90deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.dash-hero__sub {
  font-size: 1.02rem;
  line-height: 1.65;
  opacity: 0.82;
  max-width: 580px;
  margin: 0 0 28px 0;
  animation: fade-up 0.8s ease-out 0.1s both;
}
.dash-hero__cta {
  display: flex; gap: 12px; flex-wrap: wrap;
  animation: fade-up 0.9s ease-out 0.2s both;
}
.dash-hero__btn-primary {
  font-weight: 700;
  padding: 4px 18px;
}
.dash-hero__btn-secondary {
  font-weight: 600;
  padding: 4px 18px;
  border: 1px solid rgba(255,255,255,0.3);
}

/* ── SECTIONS ─────────────────────────────────────────────────────── */
.dash-section {
  max-width: 1180px;
  margin: 0 auto;
  padding: 40px 28px 8px;
}
.dash-section__head {
  margin-bottom: 18px;
}
.dash-section__eyebrow {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: #6366f1;
  background: rgba(99,102,241,0.08);
  padding: 4px 10px;
  border-radius: 999px;
}
.dash-section__title {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.4px;
  color: #0f172a;
  margin: 10px 0 0 0;
}

/* ── STAT CARDS ───────────────────────────────────────────────────── */
.stat-card {
  position: relative;
  overflow: hidden;
  border-radius: 14px !important;
  background: #fff;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  animation: fade-up 0.6s ease-out both;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 32px -10px rgba(15,23,42,0.18) !important;
}
.stat-card__accent {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
}
.stat-card__body { padding: 16px 18px 14px; }
.stat-card__top {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px;
}
.stat-card__label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #64748b;
}
.stat-card__value {
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -1.2px;
  color: #0f172a;
  line-height: 1.1;
}
.stat-card__sub {
  display: flex; align-items: center; gap: 6px;
  margin-top: 6px;
  font-size: 0.72rem;
  color: #94a3b8;
}

/* ── LINK CARDS ───────────────────────────────────────────────────── */
.link-card {
  border-radius: 14px !important;
  background: #fff;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
  animation: fade-up 0.6s ease-out both;
}
.link-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px -10px rgba(15,23,42,0.15) !important;
}
.link-card__body {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px !important;
}
.link-card__icon-wrap {
  flex: 0 0 auto;
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.link-card__text { flex: 1 1 auto; min-width: 0; }
.link-card__label {
  font-weight: 700;
  font-size: 0.94rem;
  color: #0f172a;
  line-height: 1.2;
}
.link-card__hint {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 2px;
}
.link-card__chev {
  color: #cbd5e1;
  transition: transform 0.16s, color 0.16s;
}
.link-card:hover .link-card__chev {
  transform: translateX(3px);
  color: #6366f1;
}

/* ── FOOTER ───────────────────────────────────────────────────────── */
.dash-footer {
  text-align: center;
  font-size: 0.78rem;
  color: #94a3b8;
  padding: 40px 16px 32px;
}
.dash-footer__link { color: #64748b; text-decoration: none; }
.dash-footer__link:hover { color: #6366f1; text-decoration: underline; }

/* ── DARK MODE ────────────────────────────────────────────────────── */
.body--dark .dashboard-root { background: #0b1020; }
.body--dark .dash-section__title { color: #e2e8f0; }
.body--dark .dash-section__eyebrow {
  color: #a5b4fc;
  background: rgba(165,180,252,0.10);
}
.body--dark .stat-card,
.body--dark .link-card {
  background: #0f172a !important;
  border-color: rgba(255,255,255,0.08) !important;
}
.body--dark .stat-card__value,
.body--dark .link-card__label { color: #e2e8f0; }
.body--dark .stat-card__label,
.body--dark .link-card__hint { color: #94a3b8; }
.body--dark .dash-footer { color: #64748b; }

/* ── ANIMATIONS ───────────────────────────────────────────────────── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes hero-pan {
  0%   { background-position: 0% 0%, 100% 30%, 0 0; }
  100% { background-position: 30% 10%, 70% 50%, 0 0; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .dash-hero__bg { animation: none; }
  .dash-hero__title,
  .dash-hero__sub,
  .dash-hero__cta,
  .stat-card,
  .link-card { animation: none !important; }
}

/* Responsive tweaks */
@media (max-width: 600px) {
  .dash-hero { padding: 44px 20px 56px; }
  .dash-section { padding: 32px 20px 6px; }
  .stat-card__value { font-size: 1.7rem; }
}

/* ── GUIDES SECTION ───────────────────────────────────────────────── */
.dash-section__desc {
  font-size: 0.87rem;
  color: #64748b;
  margin: 4px 0 0 0;
}
.guide-card {
  border-radius: 14px !important;
  background: #fff;
  animation: fade-up 0.6s ease-out both;
  overflow: hidden;
}
.guide-card__header-inner {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 0;
  flex: 1;
}
.guide-card__icon-wrap {
  flex: 0 0 auto;
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.guide-card__meta { flex: 1 1 auto; min-width: 0; }
.guide-card__title {
  font-weight: 700;
  font-size: 0.94rem;
  color: #0f172a;
  line-height: 1.25;
}
.guide-card__hint {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 2px;
}
.guide-card__body { padding: 16px 20px 20px !important; }
.guide-steps {
  padding-left: 0;
  list-style: none;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.guide-step {
  border-left: 3px solid #e2e8f0;
  padding-left: 14px;
}
.guide-step__title {
  font-weight: 700;
  font-size: 0.88rem;
  color: #1e293b;
  margin-bottom: 4px;
}
.guide-step__desc {
  font-size: 0.83rem;
  color: #475569;
  line-height: 1.7;
}
.guide-step__note {
  font-size: 0.78rem;
  background: rgba(14,165,233,0.06) !important;
  border-radius: 8px !important;
}

/* dark mode */
.body--dark .guide-card {
  background: #0f172a !important;
  border-color: rgba(255,255,255,0.08) !important;
}
.body--dark .guide-card__title { color: #e2e8f0; }
.body--dark .guide-step__title { color: #cbd5e1; }
.body--dark .guide-step__desc { color: #94a3b8; }
.body--dark .guide-step { border-left-color: rgba(255,255,255,0.12); }
.body--dark .dash-section__desc { color: #94a3b8; }
</style>
