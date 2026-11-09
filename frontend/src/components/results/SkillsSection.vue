<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MatchStatus, SkillMatch } from '../../types/analysis'
import { STATUS_META } from '../../utils/format'
import AppIcon from '../ui/AppIcon'
import SectionHeader from './SectionHeader.vue'

const props = defineProps<{ skills: SkillMatch[] }>()

const filter = ref<'all' | 'required' | 'preferred'>('all')
const open = ref<string | null>(null)

const visible = computed(() => props.skills.filter((s) => filter.value === 'all' || s.priority === filter.value))
const counts = computed(() => {
  const c: Record<MatchStatus, number> = { demonstrated: 0, listed: 0, related: 0, missing: 0 }
  for (const s of visible.value) c[s.status]++
  return c
})
const filters = [
  { key: 'all', label: 'All' },
  { key: 'required', label: 'Required' },
  { key: 'preferred', label: 'Nice to have' },
] as const

function toggle(s: SkillMatch) {
  if (!s.evidence.length) return
  open.value = open.value === s.skill ? null : s.skill
}
</script>

<template>
  <section id="skills" aria-labelledby="skills-heading" class="card p-6 sm:p-7">
    <SectionHeader icon="tag" title="Skills from the job posting" heading-id="skills-heading">
      <div role="group" aria-label="Filter skills" class="no-print flex gap-0.5 rounded-[10px] bg-chip p-1">
        <button
          v-for="f in filters"
          :key="f.key"
          type="button"
          class="h-8 rounded-lg px-3.5 text-[13.5px] transition-colors"
          :class="filter === f.key ? 'bg-surface font-semibold text-ink shadow-sm' : 'font-medium text-text-2 hover:text-ink'"
          :aria-pressed="filter === f.key"
          @click="filter = f.key"
        >
          {{ f.label }}
        </button>
      </div>
    </SectionHeader>

    <div class="mb-2 flex flex-wrap gap-x-5 gap-y-2 text-[13px] text-text-2">
      <span v-for="(meta, key) in STATUS_META" :key="key" class="flex items-center gap-1.5" :title="meta.explain">
        <span class="h-[9px] w-[9px] rounded-full" :class="meta.dot" />
        {{ meta.label }} ({{ counts[key] }})
      </span>
    </div>

    <p v-if="!visible.length" class="pt-3 text-sm text-text-3">No skills in this group.</p>
    <ul v-else>
      <li v-for="s in visible" :key="s.skill + s.priority" class="border-t border-line-2">
        <button
          type="button"
          class="flex w-full items-center gap-3 px-1 py-[13px] text-left"
          :class="s.evidence.length ? 'cursor-pointer' : 'cursor-default'"
          :aria-expanded="s.evidence.length ? open === s.skill : undefined"
          @click="toggle(s)"
        >
          <span class="flex min-w-0 flex-1 flex-col gap-0.5">
            <span class="text-[15px] font-semibold text-ink">{{ s.skill }}</span>
            <span class="text-[13px] text-text-3">{{ s.category }}<template v-if="s.related_to"> · you have {{ s.related_to }}</template></span>
          </span>
          <span class="hidden shrink-0 text-[12.5px] text-text-3 sm:inline">{{ s.priority === 'required' ? 'Required' : 'Nice to have' }}</span>
          <span class="pill" :class="STATUS_META[s.status].pill">{{ STATUS_META[s.status].label }}</span>
          <AppIcon name="chevronDown" class="shrink-0 text-text-4 transition-transform" :class="[open === s.skill ? 'rotate-180' : '', s.evidence.length ? '' : 'invisible']" />
        </button>
        <div v-if="open === s.skill" class="mx-1 mb-3.5 flex flex-col gap-2.5 rounded-xl border border-line-2 bg-subtle px-4 py-3.5">
          <span class="text-xs font-semibold tracking-[0.04em] text-text-3 uppercase">Found in your resume</span>
          <p v-for="(e, i) in s.evidence" :key="i" class="flex items-baseline gap-2.5 text-sm leading-normal text-text-1">
            <span class="shrink-0 rounded-md bg-line-2 px-2 py-0.5 text-xs font-semibold text-text-2 capitalize">{{ e.section }}</span>
            <span>{{ e.text }}</span>
          </p>
        </div>
      </li>
    </ul>
  </section>
</template>
