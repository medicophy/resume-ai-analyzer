<script setup lang="ts">
import type { Suggestion } from '../../types/analysis'
import { PRIORITY_PILL } from '../../utils/format'
import SectionHeader from './SectionHeader.vue'

defineProps<{ suggestions: Suggestion[] }>()
</script>

<template>
  <section id="improve" aria-labelledby="improve-heading" class="card p-6 sm:p-7">
    <SectionHeader icon="list" title="What to improve" heading-id="improve-heading">
      <span class="text-[13px] text-text-3">Most important first</span>
    </SectionHeader>
    <p v-if="!suggestions.length" class="text-sm text-text-3">Nothing major to change for this posting.</p>
    <ol v-else>
      <li v-for="(s, i) in suggestions" :key="i" class="flex flex-col gap-2 border-t border-line-2 py-3.5 sm:flex-row sm:items-start sm:gap-3.5">
        <span class="pill min-w-16 justify-center self-start" :class="PRIORITY_PILL[s.priority].cls">{{ PRIORITY_PILL[s.priority].label }}</span>
        <p class="text-[14.5px] leading-relaxed text-text-1">{{ s.message }}</p>
      </li>
    </ol>
  </section>
</template>
