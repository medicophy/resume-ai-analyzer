<script setup lang="ts">
import { computed } from 'vue'
import type { AnalyzeResponse, ComponentScore } from '../../types/analysis'
import { overviewText, scoreLabel, scoreTone, toneFill, tonePill, toneText, years } from '../../utils/format'
import ScoreRing from './ScoreRing.vue'

const props = defineProps<{ result: AnalyzeResponse; jobTitle: string | null }>()

const text = computed(() => overviewText(props.result, props.jobTitle))
const overall = computed(() => props.result.overall_score)

const bars = computed(() => {
  const b = props.result.breakdown
  const rows: { label: string; value: ComponentScore | null }[] = [
    { label: 'Skills', value: b.skills },
    { label: 'Experience', value: b.experience },
    { label: 'Education', value: b.education },
  ]
  return rows
})

const stats = computed(() => {
  const r = props.result
  const required = r.skills.filter((s) => s.priority === 'required')
  const general = r.experience.checks.find((c) => c.skill === null && c.priority === 'required')
  return {
    shown: required.filter((s) => s.status === 'demonstrated').length,
    required: required.length,
    missing: required.filter((s) => s.status === 'missing').length,
    total: r.experience.total_years,
    asked: general?.required_years ?? null,
    ats: r.ats.score,
  }
})
</script>

<template>
  <section id="overview" aria-labelledby="overview-heading" class="card flex flex-col gap-7 p-6 sm:p-7">
    <div class="flex flex-wrap items-center gap-8">
      <ScoreRing :value="overall" class="mx-auto sm:mx-0" />
      <div class="flex min-w-0 flex-[1_1_320px] flex-col gap-2.5">
        <span v-if="overall !== null" class="pill self-start text-[13px]" :class="tonePill[scoreTone(overall)]">{{ scoreLabel(overall) }}</span>
        <h1 id="overview-heading" class="font-display text-2xl leading-tight font-bold tracking-[-0.015em] text-ink sm:text-[28px]">{{ text.headline }}</h1>
        <p class="text-[15.5px] leading-relaxed text-text-2">{{ text.summary }}</p>
      </div>
    </div>

    <div class="grid gap-5 sm:grid-cols-3">
      <div v-for="row in bars" :key="row.label" class="flex flex-col gap-2">
        <div class="flex justify-between text-sm">
          <span class="font-semibold text-text-1">{{ row.label }}</span>
          <span v-if="row.value" class="text-text-3">
            <span class="font-bold" :class="toneText[scoreTone(row.value.score)]">{{ Math.round(row.value.score) }}</span>
            · {{ Math.round(row.value.weight * 100) }}%
          </span>
          <span v-else class="text-xs text-text-4">Not asked for</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-line-2">
          <div v-if="row.value" class="h-full rounded-full transition-all duration-700" :class="toneFill[scoreTone(row.value.score)]" :style="{ width: `${row.value.score}%` }" />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div class="stat">
        <p class="stat-value">{{ stats.shown }} / {{ stats.required }}</p>
        <p class="stat-label">Required skills shown</p>
      </div>
      <div class="stat">
        <p class="stat-value" :class="stats.missing ? 'text-poor' : ''">{{ stats.missing }}</p>
        <p class="stat-label">Required skill{{ stats.missing === 1 ? '' : 's' }} missing</p>
      </div>
      <div class="stat">
        <p class="stat-value">
          {{ years(stats.total) }}<span v-if="stats.asked" class="text-[15px] font-medium text-text-3"> / {{ stats.asked }}</span>
        </p>
        <p class="stat-label">Experience</p>
      </div>
      <div class="stat">
        <p class="stat-value" :class="toneText[scoreTone(stats.ats)]">{{ Math.round(stats.ats) }}</p>
        <p class="stat-label">ATS readability</p>
      </div>
    </div>
  </section>
</template>
