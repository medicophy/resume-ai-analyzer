<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { AiReview } from '../../types/analysis'
import AppIcon from '../ui/AppIcon'

defineProps<{
  enabled: boolean | null
  hasFile: boolean
  loading: boolean
  error: string | null
  review: AiReview | null
}>()
const emit = defineEmits<{ run: [] }>()

const copied = ref<number | null>(null)
async function copy(text: string, index: number) {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = index
    setTimeout(() => (copied.value = copied.value === index ? null : copied.value), 1500)
  } catch {
    /* clipboard unavailable: the text can still be selected */
  }
}
</script>

<template>
  <section id="ai" aria-labelledby="ai-heading" class="card p-6 sm:p-7">
    <div class="flex flex-wrap items-center gap-5">
      <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-soft text-accent"><AppIcon name="bulb" :size="22" /></span>
      <div class="min-w-0 flex-[1_1_360px]">
        <div class="flex items-center gap-2.5">
          <h2 id="ai-heading" class="text-[19px] font-semibold text-ink">AI suggestions</h2>
          <span class="pill bg-soft text-accent">Optional</span>
        </div>
        <p v-if="!review" class="mt-1.5 text-[14.5px] leading-relaxed text-text-2">
          A short assessment, draft rewrites of your bullet points and requirements the skill list doesn't cover.
          Sends your resume text, without email, phone or links, and the job posting to Groq.
        </p>
      </div>
      <template v-if="!review">
        <p v-if="enabled === false" class="w-full text-sm text-text-3">AI suggestions are turned off on this server.</p>
        <p v-else-if="!hasFile" class="w-full text-sm text-text-3">
          This report was restored after a page refresh, and your file isn't kept.
          <RouterLink to="/" class="btn-link">Analyze again</RouterLink> to get AI suggestions.
        </p>
        <button v-else type="button" class="btn-primary no-print h-11 text-[14.5px]" :disabled="loading || enabled === null" @click="emit('run')">
          <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
            <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
          </svg>
          {{ loading ? 'Asking the AI…' : 'Get AI suggestions' }}
        </button>
      </template>
    </div>
    <p v-if="error && !review" class="mt-4 text-sm text-poor" role="alert">{{ error }}</p>

    <div v-if="review" class="mt-5 flex flex-col gap-6">
      <p class="text-[15px] leading-relaxed text-text-1">{{ review.summary }}</p>

      <div v-if="review.rewrites.length">
        <h3 class="text-sm font-semibold text-ink">Draft bullet rewrites</h3>
        <p class="mt-0.5 mb-3 text-xs text-text-3">Only use a rewrite if every part of it is true.</p>
        <ul class="flex flex-col gap-3">
          <li v-for="(r, i) in review.rewrites" :key="i" class="rounded-xl border border-line-2 p-4 text-sm">
            <p class="text-text-3 line-through decoration-line-3">{{ r.original }}</p>
            <div class="mt-2 flex items-start justify-between gap-3">
              <p class="font-medium text-ink">{{ r.suggested }}</p>
              <button type="button" class="btn-link no-print flex shrink-0 items-center gap-1 text-[13px]" @click="copy(r.suggested, i)">
                <AppIcon :name="copied === i ? 'check' : 'copy'" :size="14" />
                {{ copied === i ? 'Copied' : 'Copy' }}
              </button>
            </div>
            <p v-if="r.reason" class="mt-2 text-text-2">{{ r.reason }}</p>
            <div v-if="r.skills.length" class="mt-2 flex flex-wrap gap-1.5">
              <span v-for="s in r.skills" :key="s" class="rounded-md bg-chip px-1.5 py-0.5 text-xs text-text-1">{{ s }}</span>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="review.extra_requirements.length">
        <h3 class="text-sm font-semibold text-ink">More requirements in the posting</h3>
        <p class="mt-0.5 mb-2 text-xs text-text-3">Found by the AI beyond the standard skill list. Whether your resume mentions each one is checked by text search.</p>
        <ul>
          <li v-for="req in review.extra_requirements" :key="req.term" class="flex items-center justify-between gap-3 border-t border-line-2 py-2.5 text-sm">
            <span class="text-text-1">
              {{ req.term }}
              <span v-if="req.priority === 'preferred'" class="ml-1 text-xs text-text-3">nice to have</span>
            </span>
            <span class="pill" :class="req.found_in_resume ? 'bg-good-bg text-good' : 'bg-poor-bg text-poor'">{{ req.found_in_resume ? 'In your resume' : 'Not found' }}</span>
          </li>
        </ul>
      </div>

      <p class="text-xs text-text-4">Generated by {{ review.model }} via Groq. AI output can be wrong; check it before using it.</p>
    </div>
  </section>
</template>
