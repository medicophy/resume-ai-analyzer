export type Tone = 'good' | 'fair' | 'poor'

export function scoreTone(score: number): Tone {
  if (score >= 75) return 'good'
  if (score >= 50) return 'fair'
  return 'poor'
}

export const toneText: Record<Tone, string> = {
  good: 'text-emerald-600 dark:text-emerald-400',
  fair: 'text-amber-600 dark:text-amber-400',
  poor: 'text-rose-600 dark:text-rose-400',
}

export const toneBar: Record<Tone, string> = {
  good: 'bg-emerald-500',
  fair: 'bg-amber-500',
  poor: 'bg-rose-500',
}

export const toneStroke: Record<Tone, string> = {
  good: 'stroke-emerald-500',
  fair: 'stroke-amber-500',
  poor: 'stroke-rose-500',
}

export function scoreLabel(score: number): string {
  if (score >= 85) return 'Excellent match'
  if (score >= 75) return 'Strong match'
  if (score >= 60) return 'Good match'
  if (score >= 45) return 'Partial match'
  return 'Weak match'
}

export function degreeLabel(level: string | null): string {
  const labels: Record<string, string> = {
    associate: "Associate degree",
    bachelor: "Bachelor's degree",
    master: "Master's degree",
    doctorate: 'Doctorate',
  }
  return level ? (labels[level] ?? level) : 'None found'
}

export function years(value: number): string {
  return `${Number.isInteger(value) ? value : value.toFixed(1)} yr${value === 1 ? '' : 's'}`
}
