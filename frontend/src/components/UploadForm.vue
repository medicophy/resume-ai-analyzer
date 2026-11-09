<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ loading: boolean }>()
const emit = defineEmits<{ submit: [file: File, jobDescription: string] }>()

const MAX_MB = 4
const MAX_JD = 30000
const ACCEPTED = ['.pdf', '.docx']

const file = ref<File | null>(null)
const jobDescription = ref('')
const fileError = ref<string | null>(null)
const dragging = ref(false)
const input = ref<HTMLInputElement | null>(null)

const jdTooLong = computed(() => jobDescription.value.length > MAX_JD)
const canSubmit = computed(
  () => !!file.value && jobDescription.value.trim().length > 0 && !jdTooLong.value && !props.loading,
)

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

function onChange(event: Event) {
  pick((event.target as HTMLInputElement).files?.[0])
}

function clearFile() {
  file.value = null
  if (input.value) input.value.value = ''
}

function submit() {
  if (canSubmit.value && file.value) emit('submit', file.value, jobDescription.value)
}

function sizeLabel(bytes: number) {
  return bytes < 1024 * 1024 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <form class="card space-y-6" @submit.prevent="submit">
    <div>
      <label class="label" for="resume-file">Resume</label>
      <div
        class="relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors"
        :class="
          dragging
            ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/40'
            : 'border-slate-300 hover:border-indigo-400 dark:border-slate-600'
        "
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
      >
        <template v-if="!file">
          <svg class="mb-2 h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 16V4m0 0-4 4m4-4 4 4M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
          </svg>
          <p class="text-sm text-slate-600 dark:text-slate-300">
            <button type="button" class="font-semibold text-indigo-600 hover:underline dark:text-indigo-400" @click="input?.click()">
              Choose a file
            </button>
            or drag it here
          </p>
          <p class="mt-1 text-xs text-slate-500">PDF or DOCX, up to {{ MAX_MB }} MB</p>
        </template>
        <div v-else class="flex w-full items-center justify-between gap-3 text-left">
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-slate-900 dark:text-slate-100">{{ file.name }}</p>
            <p class="text-xs text-slate-500">{{ sizeLabel(file.size) }}</p>
          </div>
          <button type="button" class="btn-ghost" @click="clearFile">Remove</button>
        </div>
        <input
          id="resume-file"
          ref="input"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          class="sr-only"
          @change="onChange"
        />
      </div>
      <p v-if="fileError" class="mt-2 text-sm text-rose-600" role="alert">{{ fileError }}</p>
    </div>

    <div>
      <div class="flex items-baseline justify-between">
        <label class="label" for="job-description">Job description</label>
        <span class="text-xs" :class="jdTooLong ? 'text-rose-600' : 'text-slate-500'">
          {{ jobDescription.length.toLocaleString() }} / {{ MAX_JD.toLocaleString() }}
        </span>
      </div>
      <textarea
        id="job-description"
        v-model="jobDescription"
        rows="8"
        class="input"
        placeholder="Paste the full job posting, including the requirements and nice-to-haves."
      />
    </div>

    <button type="submit" class="btn-primary w-full" :disabled="!canSubmit">
      <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
        <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
      </svg>
      {{ loading ? 'Analysing…' : 'Analyse resume' }}
    </button>
  </form>
</template>
