<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from '../ui/AppIcon'

const props = defineProps<{ fileName: string; fileSize: number; jobTitle: string | null; done: boolean }>()
const emit = defineEmits<{ cancel: [] }>()

const STEPS = [
  'Reading your resume',
  'Understanding the job posting',
  'Matching skills to your experience',
  'Checking experience and education',
  'Checking ATS readability',
]

// The server does all steps in one request, usually within a few seconds. The checklist
// advances on a timer to show what is happening and waits on the last step until the
// answer arrives.
const reached = ref(0)
let timer: number | undefined

onMounted(() => {
  timer = window.setInterval(() => {
    if (reached.value < STEPS.length - 1) reached.value += 1
  }, 650)
})
onBeforeUnmount(() => window.clearInterval(timer))

const current = computed(() => (props.done ? STEPS.length : reached.value))
const progress = computed(() => Math.round(((props.done ? STEPS.length : current.value + 0.5) / STEPS.length) * 100))
const size = computed(() => (props.fileSize < 1024 * 1024 ? `${Math.max(1, Math.round(props.fileSize / 1024))} KB` : `${(props.fileSize / 1024 / 1024).toFixed(1)} MB`))
</script>

<template>
  <section class="card-raised mx-auto flex w-full max-w-[560px] flex-col gap-6 p-6 sm:p-8" aria-labelledby="progress-heading">
    <div class="flex items-center gap-3 rounded-xl border border-line-2 bg-subtle px-3.5 py-3">
      <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-soft text-accent">
        <AppIcon name="file" :size="20" />
      </span>
      <span class="flex min-w-0 flex-col">
        <span class="truncate text-sm font-semibold text-ink">{{ fileName }}</span>
        <span class="truncate text-[13px] text-text-3">{{ size }}<template v-if="jobTitle"> · against “{{ jobTitle }}”</template></span>
      </span>
    </div>

    <div>
      <h1 id="progress-heading" class="font-display text-[28px] font-bold tracking-[-0.015em] text-ink">Analyzing your resume</h1>
      <p class="mt-1.5 text-[15px] text-text-3">This usually takes a few seconds.</p>
    </div>

    <div class="h-2 overflow-hidden rounded-full bg-line-2" role="progressbar" aria-label="Analysis progress" aria-valuemin="0" aria-valuemax="100" :aria-valuenow="progress">
      <div class="h-full rounded-full bg-accent transition-all duration-500" :style="{ width: `${progress}%` }" />
    </div>

    <ol class="flex flex-col gap-3.5" aria-live="polite">
      <li v-for="(step, i) in STEPS" :key="step" class="flex items-center gap-3 text-[15px]" :class="i < current ? 'text-text-1' : i === current ? 'font-semibold text-ink' : 'text-text-3'">
        <AppIcon v-if="i < current" name="checkCircle" :size="22" class="text-good" label="Done" />
        <svg v-else-if="i === current" width="22" height="22" viewBox="0 0 24 24" fill="none" role="img" aria-label="In progress" class="animate-spin">
          <circle cx="12" cy="12" r="9" class="stroke-line-2" stroke-width="3" />
          <path d="M21 12a9 9 0 0 0-9-9" class="stroke-accent" stroke-width="3" stroke-linecap="round" />
        </svg>
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" role="img" aria-label="Waiting">
          <circle cx="12" cy="12" r="9" class="stroke-line-3" stroke-width="2" />
        </svg>
        {{ step }}
      </li>
    </ol>

    <div class="flex justify-start border-t border-line-2 pt-4">
      <button type="button" class="rounded-md px-1 text-sm font-medium text-text-2 hover:text-ink" @click="emit('cancel')">Cancel</button>
    </div>
  </section>
</template>
