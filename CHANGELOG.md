# Changelog

Todas as alterações notáveis a este projeto serão documentadas aqui.

## [Não publicado] — Sessão de optimização, UI e bugfix

### 🐛 Bug fix — "Horas de crédito / redução" não eram guardadas

**Página:** `Distribuição de Serviço` (`/service-distribution` →
`ServiceAssignmentPage.vue`).

**Sintoma:** o campo *"Horas de crédito / redução"* no painel esquerdo
podia ser editado, mas o valor perdia-se ao trocar de professor ou
recarregar a página.

**Causa raiz:** o `v-model.number="creditHours"` actualizava apenas o
estado local (`ref(0)`); nunca era enviado para o backend. Os restantes
pontos de gravação (dialog *Componentes*, dialog *Gerir horas*,
atribuição de turmas) funcionavam correctamente.

**Correcção:** acrescentada a função `saveCreditHours()` que faz
`PUT /teachers/bulk-update` com `{id, credit_hours}` e é disparada nos
eventos `@change`, `@blur` e `@keyup.enter` do input. Não dispara em
cada tecla (evita *spam*) nem quando o valor não mudou. Mostra
*feedback* visual via *spinner* no próprio input e notificação Quasar
(`Horas de crédito guardadas (Xh)`). Mantém o `teachers store` em
sincronia para não exigir refetch.

### 🚀 Performance do solver OR-Tools (`backend/app/scheduler/engine.py`)

1. **Quebra de simetria entre ocorrências da mesma entrada de currículo**
   Ocorrências do tipo "single" e "first-of-pair" da mesma entrada são
   semanticamente intermutáveis. Sem ordenação, o solver explora `n!`
   relabelings equivalentes. Foram acrescentadas restrições estritas
   `slot_var[occ_i] < slot_var[occ_j]` (apenas no modo *fixed-teacher*).
   Impacto esperado: pesquisa **2–10× mais rápida** em horários com
   muitas disciplinas split.

2. **`AddAllDifferent` por turma (modo *fixed-teacher*)**
   Acrescentado um *global constraint* `AddAllDifferent` sobre todos os
   `slot_var` de cada turma — propagação muito mais forte (raciocínio de
   Hall) do que `AddAtMostOne` por slot. *Gated* para saltar turmas com
   entradas em *subject groups* (que podem partilhar slot por design).

3. **Restrição "sem furos nos alunos" reformulada de O(n³) para O(n)**
   A formulação antiga gerava `O(n³)` restrições por (turma, dia) via
   triplos `(j, i, k)`. Substituída por contagem de transições: define-se
   `rise = ¬prev ∧ curr` (uma transição 0→1) por par de slots consecutivos
   e impõe-se `used[0] + Σ rise ≤ 1`. Logicamente equivalente, mas com
   `O(n)` BoolVars e `O(n)` restrições — **redução ~30×** num horário
   típico de 7 tempos × 5 dias × 30 turmas (~31 k → ~1 k restrições).

4. **`cp_model_probing_level = 2` em ambas as fases**
   Presolve mais agressivo (descoberta de implicações binárias e
   minimização de cláusulas). Quase sempre paga em modelos pesados como
   horários escolares.

### 🎨 UI / UX

1. **`DashboardPage` redesenhada**
   - Hero animado com fundo *radial gradient* + textura de grão, *brand
     pill* glassmorphism, título com gradiente dourado e CTAs claros.
   - Cards de estatística com **contadores animados**, faixa de cor por
     métrica e *hover lift*.
   - Cards de acesso rápido reescritos: ícone em *colored chip*,
     hint descritiva e *chevron* que desliza no hover.
   - **Modo escuro** polido com cores específicas.
   - `prefers-reduced-motion` respeitado.
   - `data-testid` em todos os pontos interactivos.

2. **`app.scss` global**
   - Transições suaves em todas as primitivas Quasar.
   - Scrollbar custom (claro + escuro).
   - `:focus-visible` consistente para acessibilidade.
   - Transição de página discreta (fade-up).

3. **`GenerateTimetableDialog` polido**
   - Cabeçalho com gradient azul→ciano e título tipográfico.
   - Footer separado com fundo neutro para hierarquia visual clara.
   - `data-testid` em botões críticos.

### 📦 Estrutura

- Adicionado `CHANGELOG.md`.
- Nenhuma alteração de modelo de dados, *router contracts*, ou
  dependências (`requirements.txt` / `package.json`).

---

### Como verificar

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Gere um horário grande (>20 turmas) e compare o tempo de solução
(`tt.solver_status` + log de geração) face à versão anterior. Procure
nos logs:

```
Timetable N: <X> restrições de simetria adicionadas (ordenação de ocorrências).
Timetable N: AddAllDifferent aplicado a <Y> turma(s).
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Abrir `http://localhost:9000` — o Dashboard deve apresentar o novo hero
animado e contadores incrementais.
