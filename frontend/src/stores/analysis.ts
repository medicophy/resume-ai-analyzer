import { reactive } from 'vue'
import { analyzeResume, describeError, fetchAiEnabled, requestAiReview } from '../lib/api'
import type { AiReview, AnalyzeResponse } from '../types/analysis'
import { jobTitleFrom } from '../utils/format'

// The latest report survives a page refresh but not closing the tab. The resume file itself
// is never written to storage; it only lives in memory for the optional AI review.
const STORAGE_KEY = 'hirelens:report'

interface SavedReport {
  result: AnalyzeResponse
  jobTitle: string | null
  jobDescription: string
}

function load(): SavedReport | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as SavedReport) : null
  } catch {
    return null
  }
}

function save(report: SavedReport | null) {
  try {
    if (report) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(report))
    else sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    /* storage unavailable (private mode): the report just won't survive a refresh */
  }
}

const saved = load()

const state = reactive({
  result: saved?.result ?? (null as AnalyzeResponse | null),
  jobTitle: saved?.jobTitle ?? (null as string | null),
  jobDescription: saved?.jobDescription ?? '',
  file: null as File | null,
  analyzing: false,
  error: null as string | null,
  ai: {
    enabled: null as boolean | null,
    loading: false,
    error: null as string | null,
    review: null as AiReview | null,
  },
})

let analyzeController: AbortController | null = null
let aiController: AbortController | null = null

async function analyze(file: File, jobDescription: string): Promise<boolean> {
  analyzeController?.abort()
  aiController?.abort()
  analyzeController = new AbortController()
  state.analyzing = true
  state.error = null
  try {
    const result = await analyzeResume(file, jobDescription, analyzeController.signal)
    state.result = result
    state.file = file
    state.jobDescription = jobDescription
    state.jobTitle = jobTitleFrom(jobDescription)
    state.ai.review = null
    state.ai.error = null
    save({ result, jobTitle: state.jobTitle, jobDescription })
    return true
  } catch (e) {
    state.error = describeError(e)
    return false
  } finally {
    state.analyzing = false
  }
}

function cancelAnalysis() {
  analyzeController?.abort()
  state.analyzing = false
}

async function checkAi() {
  if (state.ai.enabled === null) state.ai.enabled = await fetchAiEnabled()
}

async function runAiReview() {
  if (!state.file) return
  aiController?.abort()
  aiController = new AbortController()
  state.ai.loading = true
  state.ai.error = null
  try {
    state.ai.review = await requestAiReview(state.file, state.jobDescription, aiController.signal)
  } catch (e) {
    state.ai.error = describeError(e)
  } finally {
    state.ai.loading = false
  }
}

function clearError() {
  state.error = null
}

// Components read `state`; changes go through the functions below.
export const analysis = {
  state,
  analyze,
  cancelAnalysis,
  checkAi,
  runAiReview,
  clearError,
}
