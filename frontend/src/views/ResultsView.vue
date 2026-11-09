<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import AiSection from '../components/results/AiSection.vue'
import AtsSection from '../components/results/AtsSection.vue'
import ExperienceSection from '../components/results/ExperienceSection.vue'
import ImproveSection from '../components/results/ImproveSection.vue'
import OverviewSection from '../components/results/OverviewSection.vue'
import ResultsSidebar from '../components/results/ResultsSidebar.vue'
import SkillsSection from '../components/results/SkillsSection.vue'
import { analysis } from '../stores/analysis'
import type { NavItem } from '../types/analysis'

const state = analysis.state
// The router only opens this page when a report exists.
const result = computed(() => state.result!)

const items = computed<NavItem[]>(() => {
  const r = result.value
  const list: NavItem[] = [
    { id: 'overview', label: 'Overview', icon: 'gauge' },
    {
      id: 'improve',
      label: 'What to improve',
      icon: 'list',
      badge: String(r.suggestions.length),
      badgeClass: r.suggestions.some((s) => s.priority === 'high') ? 'bg-poor-bg text-poor' : undefined,
    },
  ]
  if (r.skills.length) list.push({ id: 'skills', label: 'Skills', icon: 'tag', badge: String(r.skills.length) })
  list.push(
    { id: 'experience', label: 'Experience & education', icon: 'briefcase' },
    { id: 'ats', label: 'ATS readability', icon: 'layout', badge: String(Math.round(r.ats.score)) },
    { id: 'ai', label: 'AI suggestions', icon: 'bulb', badge: 'Optional', badgeClass: 'bg-soft text-accent' },
  )
  return list
})

// Highlight the section currently in view.
const active = ref('overview')
let observer: IntersectionObserver | null = null
onMounted(async () => {
  analysis.checkAi()
  await nextTick()
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      if (visible[0]) active.value = visible[0].target.id
    },
    { rootMargin: '-90px 0px -55% 0px' },
  )
  for (const item of items.value) {
    const el = document.getElementById(item.id)
    if (el) observer.observe(el)
  }
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="flex-1">
    <nav aria-label="Sections" class="no-print sticky top-16 z-20 flex gap-1.5 overflow-x-auto border-b border-line bg-surface px-4 py-2.5 whitespace-nowrap lg:hidden">
      <a
        v-for="item in items"
        :key="item.id"
        :href="`#${item.id}`"
        class="rounded-full px-3.5 py-2 text-sm"
        :class="active === item.id ? 'bg-soft font-semibold text-accent' : 'bg-chip font-medium text-text-2'"
      >
        {{ item.label }}
      </a>
    </nav>

    <div class="container-page flex items-start gap-8 py-6 lg:py-8">
      <ResultsSidebar :result="result" :job-title="state.jobTitle" :items="items" :active="active" />

      <div class="flex min-w-0 flex-1 flex-col gap-6">
        <div v-if="result.warnings.length" class="flex flex-col gap-1 rounded-xl border border-fair-line bg-fair-surface p-4 text-sm text-text-1" role="status">
          <p v-for="(w, i) in result.warnings" :key="i">{{ w }}</p>
        </div>

        <OverviewSection :result="result" :job-title="state.jobTitle" />
        <ImproveSection :suggestions="result.suggestions" />
        <SkillsSection v-if="result.skills.length" :skills="result.skills" />
        <ExperienceSection :experience="result.experience" :education="result.education" />
        <AtsSection :ats="result.ats" />
        <AiSection
          :enabled="state.ai.enabled"
          :has-file="!!state.file"
          :loading="state.ai.loading"
          :error="state.ai.error"
          :review="state.ai.review"
          @run="analysis.runAiReview"
        />
      </div>
    </div>
  </div>
</template>
