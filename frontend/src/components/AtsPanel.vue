<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AtsReport } from '../types/analysis'
import { scoreTone, toneText } from '../utils/format'

const props = defineProps<{ ats: AtsReport }>()
const showPassed = ref(false)

const issues = computed(() => props.ats.checks.filter((c) => c.status !== 'pass'))
const passed = computed(() => props.ats.checks.filter((c) => c.status === 'pass'))

const ICON = {
  fail: { cls: 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300', symbol: '✕', label: 'Problem' },
  warn: { cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300', symbol: '!', label: 'Warning' },
  pass: { cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300', symbol: '✓', label: 'Passed' },
} as const
</script>

<template>
  <section class="card" aria-labelledby="ats-heading">
    <div class="mb-1 flex items-baseline justify-between">
      <h2 id="ats-heading" class="section-title">ATS readability</h2>
      <span class="text-lg font-bold" :class="toneText[scoreTone(ats.score)]">{{ Math.round(ats.score) }}/100</span>
    </div>
    <p class="mb-4 text-sm text-slate-500">
      How easily applicant tracking systems can read your resume. This doesn't affect the match score.
    </p>

    <p v-if="!issues.length" class="text-sm text-emerald-700 dark:text-emerald-400">All checks passed.</p>
    <ul class="space-y-3">
      <li v-for="c in issues" :key="c.id" class="flex gap-3 text-sm">
        <span
          class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold"
          :class="ICON[c.status].cls"
          :aria-label="ICON[c.status].label"
        >{{ ICON[c.status].symbol }}</span>
        <div>
          <p class="font-medium text-slate-900 dark:text-slate-100">{{ c.label }}</p>
          <p class="text-slate-600 dark:text-slate-400">{{ c.message }}</p>
          <p v-if="c.fix" class="mt-1 text-slate-700 dark:text-slate-300"><span class="font-medium">Fix:</span> {{ c.fix }}</p>
        </div>
      </li>
    </ul>

    <div v-if="passed.length" class="mt-4 border-t border-slate-100 pt-3 dark:border-slate-800">
      <button type="button" class="btn-ghost -ml-2" :aria-expanded="showPassed" @click="showPassed = !showPassed">
        {{ showPassed ? 'Hide' : 'Show' }} {{ passed.length }} passed check{{ passed.length === 1 ? '' : 's' }}
      </button>
      <ul v-if="showPassed" class="mt-2 space-y-2">
        <li v-for="c in passed" :key="c.id" class="flex gap-3 text-sm">
          <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold" :class="ICON.pass.cls" aria-label="Passed">✓</span>
          <p class="text-slate-600 dark:text-slate-400"><span class="font-medium text-slate-800 dark:text-slate-200">{{ c.label }}:</span> {{ c.message }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>
