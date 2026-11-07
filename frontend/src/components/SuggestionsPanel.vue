<script setup lang="ts">
import type { Suggestion } from '../types/analysis'

defineProps<{ suggestions: Suggestion[] }>()

const STYLE = {
  high: { label: 'High', cls: 'bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-300' },
  medium: { label: 'Medium', cls: 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300' },
  low: { label: 'Low', cls: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
} as const
</script>

<template>
  <section class="card" aria-labelledby="sugg-heading">
    <h2 id="sugg-heading" class="section-title mb-4">What to improve</h2>
    <p v-if="!suggestions.length" class="text-sm text-slate-500">
      Nothing major to change for this posting. Nice work.
    </p>
    <ol v-else class="space-y-3">
      <li v-for="(s, i) in suggestions" :key="i" class="flex gap-3 text-sm">
        <span class="mt-0.5 h-fit shrink-0 rounded px-2 py-0.5 text-xs font-medium" :class="STYLE[s.priority].cls">
          {{ STYLE[s.priority].label }}
        </span>
        <p class="text-slate-700 dark:text-slate-300">{{ s.message }}</p>
      </li>
    </ol>
  </section>
</template>
