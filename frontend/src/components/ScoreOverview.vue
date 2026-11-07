<script setup lang="ts">
import { computed } from 'vue'
import type { AnalyzeResponse, ComponentScore } from '../types/analysis'
import { scoreLabel, scoreTone, toneBar, toneStroke, toneText } from '../utils/format'

const props = defineProps<{ result: AnalyzeResponse }>()

const RADIUS = 52
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const overall = computed(() => props.result.overall_score)
const dash = computed(() => (overall.value === null ? CIRCUMFERENCE : CIRCUMFERENCE * (1 - overall.value / 100)))

const components = computed(() => {
  const b = props.result.breakdown
  const rows: { key: string; label: string; hint: string; value: ComponentScore | null }[] = [
    { key: 'skills', label: 'Skills', hint: 'Required and nice-to-have skills found in your resume', value: b.skills },
    { key: 'experience', label: 'Experience', hint: 'Years of experience against the posting', value: b.experience },
    { key: 'education', label: 'Education', hint: 'Degree level against the posting', value: b.education },
  ]
  return rows
})

const requiredStats = computed(() => {
  const req = props.result.skills.filter((s) => s.priority === 'required')
  return {
    total: req.length,
    demonstrated: req.filter((s) => s.status === 'demonstrated').length,
    missing: req.filter((s) => s.status === 'missing').length,
  }
})
</script>

<template>
  <section class="card" aria-labelledby="score-heading">
    <h2 id="score-heading" class="sr-only">Score overview</h2>
    <div class="grid gap-8 md:grid-cols-[auto_1fr] md:items-center">
      <div class="flex flex-col items-center">
        <div class="relative h-36 w-36">
          <svg viewBox="0 0 120 120" class="h-full w-full -rotate-90" aria-hidden="true">
            <circle cx="60" cy="60" :r="RADIUS" fill="none" stroke-width="10" class="stroke-slate-200 dark:stroke-slate-700" />
            <circle
              v-if="overall !== null"
              cx="60"
              cy="60"
              :r="RADIUS"
              fill="none"
              stroke-width="10"
              stroke-linecap="round"
              :class="toneStroke[scoreTone(overall)]"
              :stroke-dasharray="CIRCUMFERENCE"
              :stroke-dashoffset="dash"
              style="transition: stroke-dashoffset 0.8s ease"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <template v-if="overall !== null">
              <span class="text-3xl font-bold" :class="toneText[scoreTone(overall)]">{{ Math.round(overall) }}</span>
              <span class="text-xs text-slate-500">out of 100</span>
            </template>
            <span v-else class="px-4 text-center text-xs text-slate-500">Not enough to score</span>
          </div>
        </div>
        <p v-if="overall !== null" class="mt-3 font-semibold text-slate-900 dark:text-slate-100">{{ scoreLabel(overall) }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ result.filename }}</p>
      </div>

      <div class="space-y-5">
        <div v-for="row in components" :key="row.key">
          <div class="mb-1 flex items-baseline justify-between gap-2 text-sm">
            <span class="font-medium text-slate-800 dark:text-slate-200" :title="row.hint">{{ row.label }}</span>
            <span v-if="row.value" class="text-slate-500">
              <span class="font-semibold" :class="toneText[scoreTone(row.value.score)]">{{ Math.round(row.value.score) }}</span>
              · {{ Math.round(row.value.weight * 100) }}% of score
            </span>
            <span v-else class="text-xs text-slate-400">Not asked for in this posting</span>
          </div>
          <div class="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <div
              v-if="row.value"
              class="h-full rounded-full transition-all duration-700"
              :class="toneBar[scoreTone(row.value.score)]"
              :style="{ width: `${row.value.score}%` }"
            />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3 pt-2 text-center">
          <div class="stat">
            <p class="stat-value">{{ requiredStats.demonstrated }}/{{ requiredStats.total }}</p>
            <p class="stat-label">Required skills shown</p>
          </div>
          <div class="stat">
            <p class="stat-value" :class="requiredStats.missing ? 'text-rose-600 dark:text-rose-400' : ''">{{ requiredStats.missing }}</p>
            <p class="stat-label">Required skills missing</p>
          </div>
          <div class="stat">
            <p class="stat-value" :class="toneText[scoreTone(result.ats.score)]">{{ Math.round(result.ats.score) }}</p>
            <p class="stat-label">ATS readability</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
