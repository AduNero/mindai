# Design

<!-- impeccable:design-schema 1 -->

## Direction: "Instrument Panel"

MindCare AI reads as a precision instrument for your own longitudinal
signal (mood, journal sentiment, assessments, chat) — not another soft
pastel wellness-app toy, and not sterile clinical-white either. Those are
this category's two ruts: the Calm/Headspace pastel-gradient-blob look,
and its "clinical trust" opposite (stock photos, checkmark icons, cold
blue-on-white). Both were deliberately avoided.

The mechanism this dramatizes: MindCare AI's real claim is an
interpretable, explainable score built from real clinical instruments
(PHQ-9, GAD-7, etc.) plus AI analysis — not vibes. The visual language
borrows from instrument readouts and lab/chart reports: tabular numerals,
hairline rules, a restrained palette with one confident accent, reserving
visual weight for moments that actually matter (a crisis flag, a
milestone) rather than spending it on routine screens.

## Color

**Strategy: Restrained** (neutrals plus one accent) — the default for an
Operate-mode product (task-first, dashboard-style), per the source
skill's own mode guidance.

- **Accent — `brand` scale** (`tailwind.config.js`): a deep pine/teal
  (`#2f6456` at 600, the primary interactive color), replacing the
  previous generic indigo-to-violet (`#4f5fee`) that's the default for
  almost every AI SaaS product right now.
- **Neutrals — `paper` scale**: warm off-white (`#faf8f4`) instead of
  stark white or cold gray for page/card backgrounds. Body text and
  borders still use Tailwind's default `gray` scale — that reads fine
  against a warm ground, so it wasn't necessary to reinvent it too.
- **Semantic colors unchanged**: `wellness.{low,moderate,good,excellent}`
  and `red-*` (crisis/danger) were deliberately left alone — these are
  safety-relevant and already correctly distinguishable; not worth
  re-testing colorblind-safety on for a palette refresh.

## Type

**IBM Plex Sans** (UI/body) + **IBM Plex Mono** (every number — scores,
chart labels, stat figures, via the `.stat-figure` utility class). IBM
Plex was designed for technical, data-dense enterprise software — a
genuine fit for "instrument panel for your own data," not an arbitrary
swap from the previous unloaded "Inter" (which, note, was never actually
loaded via a font file or CDN link before this — the app was silently
falling back to system UI fonts the whole time).

## Component language

- **Hairline over heavy shadow**: `.card` dropped its shadow and tightened
  its radius (`rounded-2xl` → `rounded-xl`) in favor of a plain 1px
  border — reads as precision instrument, not generic SaaS card-soup.
- **Tabular mono figures**: any place a number is the point (Wellness
  Score, StatCard values, chart axis labels) uses `.stat-figure`
  (`font-mono tabular-nums`) so digits read as readings and don't jitter
  horizontally as they change.
- **No emoji icons**: replaced with the existing line-icon set
  (`components/common/icons.tsx`) — emoji-as-icon is a default that reads
  as unfinished/generic at this level of product.
- **Calmer motion**: entrance animations kept but toned down (shorter
  duration, smaller translate distance) — per the product principle
  "longitudinal calm, not daily urgency" in `PRODUCT.md`.

## What this pass covered

The design system (`tailwind.config.js`, `index.css`) cascades the new
palette/type to every screen automatically via the shared `.card`/
`.btn-*`/`.input`/`brand-*` classes. Beyond the system itself, these were
redesigned directly as the flagship demonstration of the direction:

- `WellnessScoreGauge` — added the reading-scale motif (0/50/100 tick
  labels), mono figure for the score.
- `StatCard` — mono figures, tighter icon-tile radius.
- `LandingPage` — hero (flat warm background instead of a generic
  gradient wash, restrained badge copy), feature grid (line icons
  instead of emoji).
- `MoodTrendChart`, `ReportsPage`'s wellness-score chart — updated
  hardcoded chart colors (Chart.js needs literal hex, can't consume
  Tailwind classes) to match the new accent.

**Not yet redesigned**: the remaining ~50 pages/components (dashboard
detail pages, admin screens, auth pages, journal/mood/assessment/
appointment flows, AI chat page) inherit the new system automatically
through the shared classes and read consistently with it, but weren't
individually art-directed the way the flagship screens above were. A
natural next pass would work through them screen by screen applying the
same instrument-panel vocabulary (hairline treatment, mono figures for
any data point, line icons) directly rather than just inheriting tokens.

## Accessibility

Contrast target: WCAG 2.1 AA (see `PRODUCT.md`). The new `brand-600`
(`#2f6456`) against white text and the warm `paper-50`/`paper-950`
backgrounds against `gray-900`/`gray-100` text were chosen for comfortable
AA contrast, matching the previous scale's contrast class rather than
degrading it. Not independently re-audited with automated tooling in this
pass — worth doing before treating this as a finished, verified system.
