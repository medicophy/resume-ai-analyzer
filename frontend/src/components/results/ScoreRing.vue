<script setup lang="ts">
import { computed } from 'vue'
import { scoreTone, toneStroke } from '../../utils/format'

const props = withDefaults(defineProps<{ value: number | null; size?: number; stroke?: number; caption?: boolean }>(), {
  size: 168,
  stroke: 14,
  caption: true,
})

const R = 70
const C = 2 * Math.PI * R
const offset = computed(() => (props.value === null ? C : C * (1 - Math.min(100, Math.max(0, props.value)) / 100)))
const sw = computed(() => (props.stroke * 160) / props.size)
</script>

<template>
  <div class="relative shrink-0" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg :width="size" :height="size" viewBox="0 0 160 160" aria-hidden="true">
      <circle cx="80" cy="80" :r="R" fill="none" class="stroke-line-2" :stroke-width="sw" />
      <circle
        v-if="value !== null"
        cx="80"
        cy="80"
        :r="R"
        fill="none"
        :class="toneStroke[scoreTone(value)]"
        :stroke-width="sw"
        stroke-linecap="round"
        :stroke-dasharray="C"
        :stroke-dashoffset="offset"
        transform="rotate(-90 80 80)"
        style="transition: stroke-dashoffset 0.9s ease"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <template v-if="value !== null">
        <span class="font-display leading-none font-bold text-ink" :style="{ fontSize: `${Math.round(size * 0.29)}px` }">{{ Math.round(value) }}</span>
        <span v-if="caption" class="mt-1 text-[13px] text-text-3">out of 100</span>
      </template>
      <span v-else class="px-3 text-center text-xs text-text-3">No score</span>
    </div>
  </div>
</template>
