import type { AiReview, AnalyzeResponse } from '../types/analysis'

export const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000'

async function postForm<T>(path: string, file: File, jobDescription: string, signal?: AbortSignal): Promise<T> {
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

/** A readable message for the user, or null when the request was cancelled. */
export function describeError(e: unknown): string | null {
  if (e instanceof DOMException && e.name === 'AbortError') return null
  if (e instanceof TypeError) return 'Could not reach the analysis server. Check your connection and try again.'
  return (e as Error).message
}

export function analyzeResume(file: File, jobDescription: string, signal?: AbortSignal) {
  return postForm<AnalyzeResponse>('/analyze', file, jobDescription, signal)
}

export function requestAiReview(file: File, jobDescription: string, signal?: AbortSignal) {
  return postForm<AiReview>('/ai-review', file, jobDescription, signal)
}

export async function fetchAiEnabled(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/`)
    return response.ok ? Boolean((await response.json()).ai_enabled) : false
  } catch {
    return false
  }
}
