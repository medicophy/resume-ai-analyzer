import { ref } from 'vue'
import type { AiReview, AnalyzeResponse } from '../types/analysis'

export const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000'

async function postForm<T>(path: string, file: File, jobDescription: string, signal: AbortSignal): Promise<T> {
  const form = new FormData()
  form.append('file', file)
  form.append('job_description', jobDescription)
  const response = await fetch(`${API_URL}${path}`, { method: 'POST', body: form, signal })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(data?.detail ?? `The server returned an error (${response.status}).`)
  }
  return data as T
}

function describe(e: unknown): string | null {
  if (e instanceof DOMException && e.name === 'AbortError') return null
  if (e instanceof TypeError) return `Could not reach the analysis server at ${API_URL}. Is the backend running?`
  return (e as Error).message
}

export function useAnalyze() {
  const result = ref<AnalyzeResponse | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)
  let controller: AbortController | null = null

  async function analyze(file: File, jobDescription: string) {
    controller?.abort()
    controller = new AbortController()
    loading.value = true
    error.value = null
    try {
      result.value = await postForm<AnalyzeResponse>('/analyze', file, jobDescription, controller.signal)
    } catch (e) {
      const message = describe(e)
      if (message) error.value = message
    } finally {
      loading.value = false
    }
  }

  return { result, error, loading, analyze }
}

export function useAiReview() {
  const review = ref<AiReview | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)
  const enabled = ref<boolean | null>(null)
  let controller: AbortController | null = null

  async function checkEnabled() {
    try {
      const response = await fetch(`${API_URL}/`)
      enabled.value = response.ok ? Boolean((await response.json()).ai_enabled) : false
    } catch {
      enabled.value = false
    }
  }

  async function run(file: File, jobDescription: string) {
    controller?.abort()
    controller = new AbortController()
    loading.value = true
    error.value = null
    try {
      review.value = await postForm<AiReview>('/ai-review', file, jobDescription, controller.signal)
    } catch (e) {
      const message = describe(e)
      if (message) error.value = message
    } finally {
      loading.value = false
    }
  }

  function reset() {
    controller?.abort()
    review.value = null
    error.value = null
    loading.value = false
  }

  return { review, error, loading, enabled, checkEnabled, run, reset }
}
