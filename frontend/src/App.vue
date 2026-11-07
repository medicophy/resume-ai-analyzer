<script setup lang="ts">
import { nextTick, ref } from 'vue'
import AtsPanel from './components/AtsPanel.vue'
import RequirementsPanel from './components/RequirementsPanel.vue'
import ScoreOverview from './components/ScoreOverview.vue'
import SkillsPanel from './components/SkillsPanel.vue'
import SuggestionsPanel from './components/SuggestionsPanel.vue'
import UploadForm from './components/UploadForm.vue'
import { useAnalyze } from './composables/useAnalyze'

const { result, error, loading, analyze } = useAnalyze()
const resultsEl = ref<HTMLElement | null>(null)

async function onSubmit(file: File, jobDescription: string) {
  await analyze(file, jobDescription)
  if (result.value) {
    await nextTick()
    resultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80">
      <div class="mx-auto flex max-w-5xl items-center gap-3 px-4 py-4">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white" aria-hidden="true">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Resume Analyzer</h1>
          <p class="text-xs text-slate-500">See how well your resume fits a job, and what to change. Nothing is stored.</p>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl space-y-6 px-4 py-8">
      <UploadForm :loading="loading" @submit="onSubmit" />

      <div
        v-if="error"
        class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-300"
        role="alert"
      >
        {{ error }}
      </div>

      <div v-if="result" ref="resultsEl" class="scroll-mt-6 space-y-6">
        <div
          v-if="result.warnings.length"
          class="space-y-1 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200"
          role="status"
        >
          <p v-for="(w, i) in result.warnings" :key="i">{{ w }}</p>
        </div>

        <ScoreOverview :result="result" />

        <div class="grid gap-6 lg:grid-cols-2">
          <SuggestionsPanel :suggestions="result.suggestions" />
          <RequirementsPanel :experience="result.experience" :education="result.education" />
        </div>

        <SkillsPanel v-if="result.skills.length" :skills="result.skills" />
        <AtsPanel :ats="result.ats" />
      </div>
    </main>
  </div>
</template>
