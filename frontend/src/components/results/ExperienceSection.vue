<script setup lang="ts">
import type { EducationCheck, ExperienceSummary } from '../../types/analysis'
import { degreeLabel, years } from '../../utils/format'
import SectionHeader from './SectionHeader.vue'

defineProps<{ experience: ExperienceSummary; education: EducationCheck | null }>()
</script>

<template>
  <section id="experience" aria-labelledby="experience-heading" class="card p-6 sm:p-7">
    <SectionHeader icon="briefcase" title="Experience and education" heading-id="experience-heading" />
    <div class="flex flex-wrap gap-5">
      <div class="grid flex-[1_1_220px] grid-cols-2 content-start gap-3">
        <div class="stat">
          <p class="stat-value">{{ years(experience.total_years) }}</p>
          <p class="stat-label">Total experience</p>
        </div>
        <div class="stat">
          <p class="stat-value">{{ experience.roles_found }}</p>
          <p class="stat-label">Dated roles found</p>
        </div>
      </div>

      <ul class="flex flex-[2_1_360px] flex-col gap-2.5">
        <li v-for="(c, i) in experience.checks" :key="i" class="flex items-center justify-between gap-3 rounded-xl border border-line-2 px-4 py-3.5">
          <span class="flex flex-col gap-0.5">
            <span class="text-[15px] font-semibold text-ink">
              {{ c.required_years }}+ years {{ c.skill ? `of ${c.skill}` : 'of experience' }}
              <span v-if="c.priority === 'preferred'" class="text-xs font-normal text-text-3">(nice to have)</span>
            </span>
            <span class="text-[13.5px] text-text-3">Your resume shows about {{ years(c.resume_years) }}</span>
          </span>
          <span class="pill" :class="c.met ? 'bg-good-bg text-good' : 'bg-poor-bg text-poor'">{{ c.met ? 'Met' : 'Short' }}</span>
        </li>
        <li v-if="education" class="flex items-center justify-between gap-3 rounded-xl border border-line-2 px-4 py-3.5">
          <span class="flex flex-col gap-0.5">
            <span class="text-[15px] font-semibold text-ink">
              {{ degreeLabel(education.required_level) }}
              <span v-if="education.priority === 'preferred'" class="text-xs font-normal text-text-3">(preferred)</span>
            </span>
            <span class="text-[13.5px] text-text-3">
              Highest degree found: {{ degreeLabel(education.resume_level) }}<template v-if="education.equivalent_experience_ok"> · equivalent experience accepted</template>
            </span>
          </span>
          <span class="pill" :class="education.met ? 'bg-good-bg text-good' : 'bg-poor-bg text-poor'">{{ education.met ? 'Met' : 'Not met' }}</span>
        </li>
        <li v-if="!experience.checks.length && !education" class="text-sm text-text-3">
          The posting doesn't state years of experience or a degree requirement.
        </li>
      </ul>
    </div>
  </section>
</template>
