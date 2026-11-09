<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from '../ui/AppIcon'

const props = defineProps<{ error: string | null; initialJobDescription?: string }>()
const emit = defineEmits<{ submit: [file: File, jobDescription: string] }>()

const MAX_MB = 4
const MAX_JD = 30000
const ACCEPTED = ['.pdf', '.docx']

const file = ref<File | null>(null)
const jobDescription = ref(props.initialJobDescription ?? '')
const fileError = ref<string | null>(null)
const dragging = ref(false)
const input = ref<HTMLInputElement | null>(null)

const jdTooLong = computed(() => jobDescription.value.length > MAX_JD)
const canSubmit = computed(() => !!file.value && jobDescription.value.trim().length > 0 && !jdTooLong.value)

function pick(candidate: File | undefined) {
  fileError.value = null
  if (!candidate) return
  const name = candidate.name.toLowerCase()
  if (!ACCEPTED.some((ext) => name.endsWith(ext))) {
    fileError.value = 'Please choose a PDF or DOCX file.'
    return
  }
  if (candidate.size > MAX_MB * 1024 * 1024) {
    fileError.value = `The file is larger than ${MAX_MB} MB.`
    return
  }
  file.value = candidate
}

function onDrop(event: DragEvent) {
  dragging.value = false
  pick(event.dataTransfer?.files[0])
}

function clearFile() {
  file.value = null
  if (input.value) input.value.value = ''
}

function submit() {
  if (canSubmit.value && file.value) emit('submit', file.value, jobDescription.value)
}

function sizeLabel(bytes: number) {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <form class="card-raised flex flex-col gap-5 p-6 sm:p-7" aria-labelledby="analyze-heading" @submit.prevent="submit">
    <div>
      <h2 id="analyze-heading" class="text-[19px] font-semibold text-ink">Analyze your resume</h2>
      <p class="mt-1 text-sm text-text-3">Takes a few seconds. No account needed.</p>
    </div>

    <div class="flex flex-col gap-2">
      <div class="flex items-baseline justify-between">
        <span id="resume-label" class="text-sm font-semibold text-text-1">Resume</span>
        <span class="text-[12.5px] text-text-3">PDF or DOCX · up to {{ MAX_MB }} MB</span>
      </div>
      <div
        class="rounded-xl border-[1.5px] border-dashed transition-colors"
        :class="dragging ? 'border-accent bg-soft' : 'border-line-3 bg-subtle hover:border-accent'"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
      >
        <label v-if="!file" for="resume-file" class="flex cursor-pointer items-center gap-4 px-5 py-[18px]">
          <span class="flex h-[46px] w-[46px] shrink-0 items-center justify-center rounded-xl border border-line bg-surface text-accent">
            <AppIcon name="upload" :size="22" />
          </span>
          <span class="flex flex-col gap-0.5">
            <span class="text-[15px] font-semibold text-ink">Drag and drop your resume</span>
            <span class="text-sm text-text-3">or <span class="font-semibold text-accent underline underline-offset-[3px]">browse files</span></span>
          </span>
        </label>
        <div v-else class="flex items-center gap-4 px-5 py-[18px]">
          <span class="flex h-[46px] w-[46px] shrink-0 items-center justify-center rounded-xl bg-soft text-accent">
            <AppIcon name="file" :size="22" />
          </span>
          <span class="flex min-w-0 flex-1 flex-col gap-0.5">
            <span class="truncate text-[15px] font-semibold text-ink">{{ file.name }}</span>
            <span class="text-sm text-text-3">{{ sizeLabel(file.size) }}</span>
          </span>
          <button type="button" class="btn-link text-sm" @click="clearFile">Change</button>
        </div>
        <input
          id="resume-file"
          ref="input"
          type="file"
          aria-labelledby="resume-label"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          class="sr-only"
          @change="pick(($event.target as HTMLInputElement).files?.[0])"
        />
      </div>
      <p v-if="fileError" class="text-sm text-poor" role="alert">{{ fileError }}</p>
    </div>

    <div class="flex flex-col gap-2">
      <div class="flex items-baseline justify-between">
        <label for="job-description" class="text-sm font-semibold text-text-1">Job description</label>
        <span class="text-[12.5px]" :class="jdTooLong ? 'text-poor' : 'text-text-3'">
          {{ jobDescription.length.toLocaleString() }} / {{ MAX_JD.toLocaleString() }}
        </span>
      </div>
      <textarea
        id="job-description"
        v-model="jobDescription"
        rows="8"
        class="input min-h-[180px] resize-y lg:min-h-[200px]"
        placeholder="Paste the full job posting, including the requirements and nice-to-haves."
      />
    </div>

    <p v-if="error" class="rounded-xl border border-poor-bg bg-poor-bg px-4 py-3 text-sm text-poor" role="alert">{{ error }}</p>

    <button type="submit" class="btn-primary h-[50px] text-[15px]" :disabled="!canSubmit">
      Analyze resume
      <AppIcon name="arrowRight" />
    </button>

    <p class="flex items-start gap-2 text-[12.5px] leading-relaxed text-text-3">
      <AppIcon name="lock" :size="15" class="mt-px shrink-0" />
      Your resume is processed in memory and discarded right after. AI suggestions are optional and only run when you ask.
    </p>
  </form>
</template>
