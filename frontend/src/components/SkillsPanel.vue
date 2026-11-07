<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MatchStatus, SkillMatch } from '../types/analysis'

const props = defineProps<{ skills: SkillMatch[] }>()

const STATUS: Record<MatchStatus, { label: string; badge: string; dot: string; explain: string }> = {
  demonstrated: {
    label: 'Shown in experience',
    badge: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300',
    dot: 'bg-emerald-500',
    explain: 'Used in your experience or projects. Full credit.',
  },
  listed: {
    label: 'Only listed',
    badge: 'bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-300',
    dot: 'bg-sky-500',
    explain: 'Appears in your skills list or summary but not in a role. Partial credit.',
  },
  related: {
    label: 'Related skill',
    badge: 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300',
    dot: 'bg-amber-500',
    explain: 'Not found, but a related skill is. Small credit.',
  },
  missing: {
    label: 'Missing',
    badge: 'bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-300',
    dot: 'bg-rose-500',
    explain: 'Not found in your resume.',
  },
}

const filter = ref<'all' | 'required' | 'preferred'>('all')
const open = ref<string | null>(null)

const visible = computed(() =>
  props.skills.filter((s) => filter.value === 'all' || s.priority === filter.value),
)

const counts = computed(() => {
  const c: Record<MatchStatus, number> = { demonstrated: 0, listed: 0, related: 0, missing: 0 }
  for (const s of visible.value) c[s.status]++
  return c
})

function toggle(skill: SkillMatch) {
  if (!skill.evidence.length) return
  open.value = open.value === skill.skill ? null : skill.skill
}
</script>

<template>
  <section class="card" aria-labelledby="skills-heading">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h2 id="skills-heading" class="section-title">Skills from the job posting</h2>
      <div class="flex rounded-lg bg-slate-100 p-1 text-sm dark:bg-slate-800" role="group" aria-label="Filter skills">
        <button
          v-for="opt in (['all', 'required', 'preferred'] as const)"
          :key="opt"
          type="button"
          class="rounded-md px-3 py-1 capitalize transition-colors"
          :class="filter === opt ? 'bg-white font-medium shadow-sm dark:bg-slate-700' : 'text-slate-600 dark:text-slate-400'"
          :aria-pressed="filter === opt"
          @click="filter = opt"
        >
          {{ opt === 'preferred' ? 'Nice to have' : opt }}
        </button>
      </div>
    </div>

    <div class="mb-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-600 dark:text-slate-400">
      <span v-for="(meta, key) in STATUS" :key="key" class="flex items-center gap-1.5" :title="meta.explain">
        <span class="h-2 w-2 rounded-full" :class="meta.dot" />
        {{ meta.label }} ({{ counts[key] }})
      </span>
    </div>

    <p v-if="!visible.length" class="text-sm text-slate-500">No skills in this group.</p>
    <ul v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <li v-for="s in visible" :key="s.skill + s.priority">
        <button
          type="button"
          class="flex w-full items-center justify-between gap-3 py-3 text-left"
          :class="s.evidence.length ? 'cursor-pointer' : 'cursor-default'"
          :aria-expanded="s.evidence.length ? open === s.skill : undefined"
          @click="toggle(s)"
        >
          <div class="min-w-0">
            <p class="font-medium text-slate-900 dark:text-slate-100">
              {{ s.skill }}
              <span v-if="s.priority === 'preferred'" class="ml-1 text-xs font-normal text-slate-500">nice to have</span>
            </p>
            <p class="text-xs text-slate-500">
              {{ s.category }}<template v-if="s.related_to"> · you have {{ s.related_to }}</template>
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <span class="rounded-full px-2.5 py-0.5 text-xs font-medium" :class="STATUS[s.status].badge">
              {{ STATUS[s.status].label }}
            </span>
            <svg
              v-if="s.evidence.length"
              class="h-4 w-4 text-slate-400 transition-transform"
              :class="open === s.skill ? 'rotate-180' : ''"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.17l3.71-3.94a.75.75 0 1 1 1.08 1.04l-4.25 4.5a.75.75 0 0 1-1.08 0l-4.25-4.5a.75.75 0 0 1 .02-1.06Z" clip-rule="evenodd" />
            </svg>
          </div>
        </button>
        <div v-if="open === s.skill" class="mb-3 space-y-2 rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Found in your resume</p>
          <blockquote v-for="(e, i) in s.evidence" :key="i" class="text-sm text-slate-700 dark:text-slate-300">
            <span class="mr-2 rounded bg-slate-200 px-1.5 py-0.5 text-xs capitalize text-slate-600 dark:bg-slate-700 dark:text-slate-300">{{ e.section }}</span>
            {{ e.text }}
          </blockquote>
        </div>
      </li>
    </ul>
  </section>
</template>
