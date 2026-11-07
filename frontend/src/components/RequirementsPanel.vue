<script setup lang="ts">
import type { EducationCheck, ExperienceSummary } from '../types/analysis'
import { degreeLabel, years } from '../utils/format'

defineProps<{ experience: ExperienceSummary; education: EducationCheck | null }>()
</script>

<template>
  <section class="card" aria-labelledby="req-heading">
    <h2 id="req-heading" class="section-title mb-4">Experience and education</h2>

    <div class="mb-4 grid grid-cols-2 gap-3">
      <div class="stat">
        <p class="stat-value">{{ years(experience.total_years) }}</p>
        <p class="stat-label">Total experience found</p>
      </div>
      <div class="stat">
        <p class="stat-value">{{ experience.roles_found }}</p>
        <p class="stat-label">Dated roles found</p>
      </div>
    </div>

    <ul class="space-y-2">
      <li
        v-for="(c, i) in experience.checks"
        :key="i"
        class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700"
      >
        <div>
          <p class="font-medium text-slate-900 dark:text-slate-100">
            {{ c.required_years }}+ years {{ c.skill ? `of ${c.skill}` : 'of experience' }}
            <span v-if="c.priority === 'preferred'" class="text-xs font-normal text-slate-500">(nice to have)</span>
          </p>
          <p class="text-slate-500">Your resume shows about {{ years(c.resume_years) }}</p>
        </div>
        <span class="pill" :class="c.met ? 'pill-pass' : 'pill-fail'">{{ c.met ? 'Met' : 'Short' }}</span>
      </li>

      <li
        v-if="education"
        class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700"
      >
        <div>
          <p class="font-medium text-slate-900 dark:text-slate-100">
            {{ degreeLabel(education.required_level) }}
            <span v-if="education.priority === 'preferred'" class="text-xs font-normal text-slate-500">(preferred)</span>
          </p>
          <p class="text-slate-500">
            Highest degree found: {{ degreeLabel(education.resume_level) }}
            <template v-if="education.equivalent_experience_ok"> · equivalent experience accepted</template>
          </p>
        </div>
        <span class="pill" :class="education.met ? 'pill-pass' : 'pill-fail'">{{ education.met ? 'Met' : 'Not met' }}</span>
      </li>

      <li v-if="!experience.checks.length && !education" class="text-sm text-slate-500">
        The posting doesn't state years of experience or a degree requirement.
      </li>
    </ul>
  </section>
</template>
