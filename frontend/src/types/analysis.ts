// Mirrors backend/models/schemas.py

export type Priority = 'required' | 'preferred'
export type MatchStatus = 'demonstrated' | 'listed' | 'related' | 'missing'

export interface Evidence {
  section: string
  text: string
}

export interface SkillMatch {
  skill: string
  category: string
  priority: Priority
  status: MatchStatus
  related_to: string | null
  evidence: Evidence[]
}

export interface ComponentScore {
  score: number
  weight: number
}

export interface ScoreBreakdown {
  skills: ComponentScore | null
  experience: ComponentScore | null
  education: ComponentScore | null
}

export interface YearsCheck {
  skill: string | null
  required_years: number
  resume_years: number
  priority: Priority
  met: boolean
}

export interface ExperienceSummary {
  total_years: number
  roles_found: number
  checks: YearsCheck[]
}

export interface EducationCheck {
  required_level: string
  resume_level: string | null
  priority: Priority
  equivalent_experience_ok: boolean
  met: boolean
}

export interface Suggestion {
  priority: 'high' | 'medium' | 'low'
  message: string
  skill: string | null
}

export interface AtsCheck {
  id: string
  label: string
  status: 'pass' | 'warn' | 'fail'
  severity: 'critical' | 'major' | 'minor'
  message: string
  fix: string | null
}

export interface AtsReport {
  score: number
  checks: AtsCheck[]
}

export interface ExtractionInfo {
  file_type: 'pdf' | 'docx'
  page_count: number
  char_count: number
  quality: 'good' | 'low' | 'empty'
}

export interface AnalyzeResponse {
  filename: string
  overall_score: number | null
  breakdown: ScoreBreakdown
  skills: SkillMatch[]
  experience: ExperienceSummary
  education: EducationCheck | null
  suggestions: Suggestion[]
  warnings: string[]
  extraction: ExtractionInfo
  ats: AtsReport
}
