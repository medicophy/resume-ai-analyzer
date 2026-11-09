import type { AnalyzeResponse, MatchStatus } from '../types/analysis'

export type Tone = 'good' | 'fair' | 'poor'

export function scoreTone(score: number): Tone {
  if (score >= 75) return 'good'
  if (score >= 50) return 'fair'
  return 'poor'
}

// Full class names (not built from parts) so Tailwind can see them.
export const toneText: Record<Tone, string> = { good: 'text-good', fair: 'text-fair', poor: 'text-poor' }
export const toneFill: Record<Tone, string> = { good: 'bg-good-fill', fair: 'bg-fair-fill', poor: 'bg-poor-fill' }
export const toneStroke: Record<Tone, string> = { good: 'stroke-good-fill', fair: 'stroke-fair-fill', poor: 'stroke-poor-fill' }
export const tonePill: Record<Tone, string> = { good: 'bg-good-bg text-good', fair: 'bg-fair-bg text-fair', poor: 'bg-poor-bg text-poor' }

export function scoreLabel(score: number): string {
  if (score >= 85) return 'Excellent match'
  if (score >= 75) return 'Strong match'
  if (score >= 60) return 'Good match'
  if (score >= 45) return 'Partial match'
  return 'Weak match'
}

export const STATUS_META: Record<MatchStatus, { label: string; pill: string; dot: string; explain: string }> = {
  demonstrated: { label: 'Shown in experience', pill: 'bg-good-bg text-good', dot: 'bg-good-fill', explain: 'Used in your experience or projects. Full credit.' },
  listed: { label: 'Only listed', pill: 'bg-info-bg text-info', dot: 'bg-info-fill', explain: 'In your skills list or summary, but not shown in a role. Partial credit.' },
  related: { label: 'Related skill', pill: 'bg-fair-bg text-fair', dot: 'bg-fair-fill', explain: 'Not found, but a related skill is. Small credit.' },
  missing: { label: 'Missing', pill: 'bg-poor-bg text-poor', dot: 'bg-poor-fill', explain: 'Not found in your resume.' },
}

export const PRIORITY_PILL = {
  high: { label: 'High', cls: 'bg-poor-bg text-poor' },
  medium: { label: 'Medium', cls: 'bg-fair-bg text-fair' },
  low: { label: 'Low', cls: 'bg-chip text-text-1' },
} as const

export function degreeLabel(level: string | null): string {
  const labels: Record<string, string> = {
    associate: 'Associate degree',
    bachelor: "Bachelor's degree",
    master: "Master's degree",
    doctorate: 'Doctorate',
  }
  return level ? (labels[level] ?? level) : 'None found'
}

export function years(value: number): string {
  return `${Number.isInteger(value) ? value : value.toFixed(1)} yr${value === 1 ? '' : 's'}`
}

/** The posting's first short line, which is usually the job title. */
export function jobTitleFrom(jobDescription: string): string | null {
  const first = jobDescription.split(/\r?\n/).map((l) => l.trim()).find(Boolean)
  if (!first || first.length > 80 || /[.!?:]$/.test(first) || first.split(/\s+/).length > 10) return null
  return first.replace(/^(job title|position|role)\s*[:-]\s*/i, '')
}

function joinList(items: string[]): string {
  if (items.length <= 1) return items.join('')
  return `${items.slice(0, -1).join(', ')} and ${items[items.length - 1]}`
}

/** Headline and one-paragraph summary built from the rule-based results (no AI involved). */
export function overviewText(result: AnalyzeResponse, jobTitle: string | null) {
  const score = result.overall_score
  const required = result.skills.filter((s) => s.priority === 'required')
  const shown = required.filter((s) => s.status === 'demonstrated').length
  const missing = required.filter((s) => s.status === 'missing').map((s) => s.skill)
  const generalYears = result.experience.checks.find((c) => c.skill === null && c.priority === 'required')
  const yearsShort = generalYears && !generalYears.met ? generalYears : null
  const degreeShort = result.education && !result.education.met && result.education.priority === 'required'

  const gaps = missing.length + (yearsShort ? 1 : 0) + (degreeShort ? 1 : 0)
  let fit = 'Not enough to score'
  if (score !== null) {
    fit = score >= 85 ? 'An excellent fit' : score >= 75 ? 'A strong fit' : score >= 60 ? 'A good fit' : score >= 45 ? 'A partial fit' : 'A weak fit'
  }
  const target = jobTitle ? ` for ${jobTitle}` : ' for this job'
  const tail = score === null ? '' : gaps === 0 ? ', with no major gaps' : `, with ${gaps} gap${gaps === 1 ? '' : 's'} to close`
  const headline = score === null ? `${fit}${target}` : `${fit}${target}${tail}`

  const listed = required.filter((s) => s.status === 'listed').length
  const parts: string[] = []
  if (required.length) {
    if (shown === required.length) {
      parts.push(`You show all ${required.length} required skills in your work experience.`)
    } else {
      const listedPart = listed ? `, and list ${listed} only in your skills section` : ''
      parts.push(`You show ${shown} of ${required.length} required skills in your work experience${listedPart}.`)
    }
  }
  const issues: string[] = []
  if (missing.length) {
    const named = missing.length > 4 ? [...missing.slice(0, 3), `${missing.length - 3} more`] : missing
    issues.push(`${joinList(named)} ${missing.length === 1 ? 'is' : 'are'} missing`)
  }
  if (yearsShort) {
    const have = Number.isInteger(yearsShort.resume_years) ? yearsShort.resume_years : yearsShort.resume_years.toFixed(1)
    issues.push(`the dates on your resume add up to about ${have} of the ${yearsShort.required_years} years asked for`)
  }
  if (degreeShort && result.education) issues.push(`the posting asks for a ${degreeLabel(result.education.required_level).toLowerCase()}`)
  if (issues.length) {
    const sentence = joinList(issues)
    parts.push(sentence.charAt(0).toUpperCase() + sentence.slice(1) + '.')
  } else if (score !== null) {
    parts.push('Your resume covers what this posting asks for.')
  }
  return { headline, summary: parts.join(' ') }
}
