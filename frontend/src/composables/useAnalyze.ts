import { ref } from 'vue'
import type { AnalyzeResponse } from '../types/analysis'

const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000'

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

    const form = new FormData()
    form.append('file', file)
    form.append('job_description', jobDescription)

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: form,
        signal: controller.signal,
      })
      const data = await response.json().catch(() => null)
      if (!response.ok) {
        throw new Error(data?.detail ?? `The server returned an error (${response.status}).`)
      }
      result.value = data as AnalyzeResponse
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return
      error.value =
        e instanceof TypeError
          ? `Could not reach the analysis server at ${API_URL}. Is the backend running?`
          : (e as Error).message
    } finally {
      loading.value = false
    }
  }

  function reset() {
    controller?.abort()
    result.value = null
    error.value = null
    loading.value = false
  }

  return { result, error, loading, analyze, reset }
}
