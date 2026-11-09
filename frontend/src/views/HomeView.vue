<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AnalyzingCard from '../components/home/AnalyzingCard.vue'
import UploadCard from '../components/home/UploadCard.vue'
import AppIcon from '../components/ui/AppIcon'
import { analysis } from '../stores/analysis'
import { jobTitleFrom } from '../utils/format'

const router = useRouter()
const state = analysis.state
const pending = ref<{ name: string; size: number; jobTitle: string | null } | null>(null)
const finished = ref(false)

async function onSubmit(file: File, jobDescription: string) {
  pending.value = { name: file.name, size: file.size, jobTitle: jobTitleFrom(jobDescription) }
  finished.value = false
  const ok = await analysis.analyze(file, jobDescription)
  if (ok) {
    finished.value = true
    // Let the checklist complete visibly before moving on.
    await new Promise((r) => setTimeout(r, 350))
    await router.push({ name: 'results' })
  }
  pending.value = null
}

function cancel() {
  analysis.cancelAnalysis()
  pending.value = null
}

const features = [
  { icon: 'shield', title: 'Private by design', text: 'Your file is read in memory and never stored.' },
  { icon: 'target', title: 'Evidence, not guesswork', text: 'Every matched skill points to the line in your resume that proves it.' },
  { icon: 'layout', title: 'ATS readability check', text: "Spot layouts and formatting that applicant tracking systems can't read." },
] as const
</script>

<template>
  <div class="flex flex-1 items-center">
    <div v-if="pending" class="container-page py-10">
      <AnalyzingCard :file-name="pending.name" :file-size="pending.size" :job-title="pending.jobTitle" :done="finished" @cancel="cancel" />
    </div>

    <div v-else class="container-page flex flex-wrap items-center gap-x-16 gap-y-10 py-8 lg:py-10">
      <section class="min-w-0 flex-[1_1_420px]">
        <span class="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 text-[13px] font-medium text-text-1">
          <span class="h-2 w-2 rounded-full bg-accent" />
          Free · No sign-up · Nothing stored
        </span>
        <h1 class="mt-5 mb-4 font-display text-[34px] leading-[1.1] font-bold tracking-[-0.025em] text-ink sm:text-[44px] xl:text-[50px] xl:leading-[1.08]">
          See how well your resume fits the job, before a recruiter does.
        </h1>
        <p class="max-w-[540px] text-[17px] leading-relaxed text-text-2 sm:text-lg">
          Upload your resume and paste the job posting. You get an honest match score, the skills you show and the ones you're missing, and the changes that matter most.
        </p>

        <ul class="mt-8 flex flex-col gap-4">
          <li v-for="f in features" :key="f.title" class="flex items-start gap-3.5">
            <span class="flex h-[38px] w-[38px] shrink-0 items-center justify-center rounded-[10px] border border-line bg-surface text-accent">
              <AppIcon :name="f.icon" :size="19" />
            </span>
            <span class="flex flex-col gap-0.5">
              <span class="text-[15px] font-semibold text-ink">{{ f.title }}</span>
              <span class="text-sm text-text-3">{{ f.text }}</span>
            </span>
          </li>
        </ul>

        <ol aria-label="How it works" class="mt-8 flex flex-wrap items-center gap-x-[18px] gap-y-3 border-t border-line pt-[22px]">
          <template v-for="(step, i) in ['Upload resume', 'Paste the job posting', 'Get your report']" :key="step">
            <li v-if="i > 0" aria-hidden="true" class="flex text-text-4"><AppIcon name="chevronRight" :size="16" /></li>
            <li class="flex items-center gap-2.5 text-sm font-medium text-text-1">
              <span class="flex h-[26px] w-[26px] items-center justify-center rounded-full bg-soft text-[13px] font-bold text-accent">{{ i + 1 }}</span>
              {{ step }}
            </li>
          </template>
        </ol>
      </section>

      <div class="min-w-0 flex-[1_1_480px]">
        <UploadCard :error="state.error" :initial-job-description="state.jobDescription" @submit="onSubmit" />
      </div>
    </div>
  </div>
</template>
