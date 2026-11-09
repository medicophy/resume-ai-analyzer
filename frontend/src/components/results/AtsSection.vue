<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AtsReport } from '../../types/analysis'
import { scoreTone, toneText } from '../../utils/format'
import AppIcon from '../ui/AppIcon'
import SectionHeader from './SectionHeader.vue'

const props = defineProps<{ ats: AtsReport }>()
const showPassed = ref(false)

const issues = computed(() => props.ats.checks.filter((c) => c.status !== 'pass'))
const passed = computed(() => props.ats.checks.filter((c) => c.status === 'pass'))
</script>

<template>
  <section id="ats" aria-labelledby="ats-heading" class="card p-6 sm:p-7">
    <SectionHeader icon="layout" title="ATS readability" heading-id="ats-heading">
      <span class="font-display text-2xl font-bold" :class="toneText[scoreTone(ats.score)]">{{ Math.round(ats.score) }}<span class="text-[15px] text-text-3">/100</span></span>
    </SectionHeader>
    <p class="-mt-2 mb-5 text-sm text-text-3">How easily applicant tracking systems can read your file. It doesn't change the match score.</p>

    <p v-if="!issues.length" class="text-sm font-medium text-good">All checks passed.</p>
    <ul class="flex flex-col gap-3">
      <li
        v-for="c in issues"
        :key="c.id"
        class="flex gap-3.5 rounded-xl border p-4"
        :class="c.status === 'fail' ? 'border-poor-bg bg-poor-bg/40' : 'border-fair-line bg-fair-surface'"
      >
        <AppIcon name="alert" :size="20" class="mt-px shrink-0" :class="c.status === 'fail' ? 'text-poor' : 'text-fair'" :label="c.status === 'fail' ? 'Problem' : 'Warning'" />
        <div class="flex flex-col gap-1">
          <span class="text-[15px] font-semibold text-ink">{{ c.label }}</span>
          <span class="text-sm text-text-2">{{ c.message }}</span>
          <span v-if="c.fix" class="text-sm text-text-1"><span class="font-semibold">Fix:</span> {{ c.fix }}</span>
        </div>
      </li>
    </ul>

    <div v-if="passed.length" class="mt-3">
      <button type="button" class="btn-link no-print px-2 py-2 text-sm" :aria-expanded="showPassed" @click="showPassed = !showPassed">
        {{ showPassed ? 'Hide' : 'Show' }} {{ passed.length }} passed check{{ passed.length === 1 ? '' : 's' }}
      </button>
      <ul v-if="showPassed" class="mt-1 flex flex-col gap-2">
        <li v-for="c in passed" :key="c.id" class="flex gap-3 text-sm">
          <AppIcon name="checkCircle" :size="18" class="mt-px shrink-0 text-good" label="Passed" />
          <p class="text-text-2"><span class="font-medium text-text-1">{{ c.label }}:</span> {{ c.message }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>
