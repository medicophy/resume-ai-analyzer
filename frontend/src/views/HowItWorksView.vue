<script setup lang="ts">
import { RouterLink } from 'vue-router'

const weights = [
  { name: 'Skills', weight: '60%', text: 'Required skills count for 75% of this part and nice-to-have skills for 25%. A skill shown in your experience earns full credit, one only listed earns 60%, a related skill 35%, and a missing skill nothing.' },
  { name: 'Experience', weight: '25%', text: 'Years of experience from the dates on your resume, against each requirement in the posting. Overlapping jobs count once, and education dates are excluded.' },
  { name: 'Education', weight: '15%', text: "Your highest degree against the posting's requirement, including \"or equivalent experience\"." },
]
</script>

<template>
  <div class="container-page max-w-[880px] py-10">
    <h1 class="font-display text-[34px] font-bold tracking-[-0.02em] text-ink">How scoring works</h1>
    <p class="mt-3 text-[17px] leading-relaxed text-text-2">
      HireLens reads the job posting to find what it asks for, then looks for evidence of each requirement in your resume.
      The score is rule-based, so the same resume and posting always get the same result.
    </p>

    <div class="card mt-8 divide-y divide-line-2">
      <div v-for="w in weights" :key="w.name" class="flex flex-col gap-1 p-6 sm:flex-row sm:gap-6">
        <div class="flex w-40 shrink-0 items-baseline justify-between sm:block">
          <p class="text-[15px] font-semibold text-ink">{{ w.name }}</p>
          <p class="font-display text-2xl font-bold text-accent">{{ w.weight }}</p>
        </div>
        <p class="text-[15px] leading-relaxed text-text-2">{{ w.text }}</p>
      </div>
    </div>

    <div class="mt-8 flex flex-col gap-4 text-[15px] leading-relaxed text-text-2">
      <p>
        <span class="font-semibold text-ink">Parts that don't apply are left out.</span>
        If a posting doesn't mention a degree, education isn't scored and the other weights are scaled up.
      </p>
      <p>
        <span class="font-semibold text-ink">Unrelated experience can't hide a poor fit.</span>
        If fewer than half of the required skills match, the overall score is capped at the skills score plus 20.
      </p>
      <p>
        <span class="font-semibold text-ink">ATS readability is scored separately.</span>
        It checks how easily applicant tracking systems can read your file, and doesn't change the match score.
      </p>
      <p>
        <span class="font-semibold text-ink">AI suggestions are optional.</span>
        They add advice and draft rewrites, but never change any score.
      </p>
    </div>

    <RouterLink to="/" class="btn-primary mt-10 h-12">Analyze a resume</RouterLink>
  </div>
</template>
