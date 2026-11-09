<script setup lang="ts">
import type { AnalyzeResponse, NavItem } from '../../types/analysis'
import { scoreLabel, scoreTone, toneText } from '../../utils/format'
import AppIcon from '../ui/AppIcon'
import ScoreRing from './ScoreRing.vue'

defineProps<{ result: AnalyzeResponse; jobTitle: string | null; items: NavItem[]; active: string }>()

function print() {
  window.print()
}
</script>

<template>
  <aside aria-label="Report navigation" class="no-print hidden w-[272px] shrink-0 lg:block">
    <div class="sticky top-[88px] flex flex-col gap-4">
      <div class="card flex flex-col gap-3.5 p-[18px]">
        <div class="flex items-center gap-3.5">
          <ScoreRing :value="result.overall_score" :size="64" :stroke="7" :caption="false" />
          <div class="flex min-w-0 flex-col gap-0.5">
            <span v-if="result.overall_score !== null" class="text-[15px] font-semibold" :class="toneText[scoreTone(result.overall_score)]">{{ scoreLabel(result.overall_score) }}</span>
            <span class="truncate text-[13px] text-text-3">{{ jobTitle ?? 'This job' }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2 rounded-[10px] bg-subtle px-3 py-2.5 text-[13px] text-text-2">
          <AppIcon name="file" :size="16" class="shrink-0" />
          <span class="truncate">{{ result.filename }}</span>
        </div>
      </div>

      <nav aria-label="Sections" class="card flex flex-col gap-0.5 p-2">
        <a
          v-for="item in items"
          :key="item.id"
          :href="`#${item.id}`"
          class="flex items-center gap-2.5 rounded-[10px] px-3 py-2.5 text-sm transition-colors"
          :class="active === item.id ? 'bg-soft font-semibold text-accent' : 'font-medium text-text-1 hover:bg-subtle'"
          :aria-current="active === item.id ? 'true' : undefined"
        >
          <AppIcon :name="item.icon" />
          <span class="flex-1">{{ item.label }}</span>
          <span v-if="item.badge" class="min-w-[22px] rounded-full px-[7px] py-px text-center text-xs font-semibold" :class="item.badgeClass ?? 'bg-chip text-text-1'">{{ item.badge }}</span>
        </a>
      </nav>

      <button type="button" class="btn-secondary h-[42px] text-sm" @click="print">
        <AppIcon name="download" :size="16" />
        Save report as PDF
      </button>
      <p class="flex gap-2 px-0.5 text-[12.5px] leading-relaxed text-text-3">
        <AppIcon name="lock" :size="14" class="mt-0.5 shrink-0" />
        This report lives only in this browser tab. Nothing was stored on our servers.
      </p>
    </div>
  </aside>
</template>
