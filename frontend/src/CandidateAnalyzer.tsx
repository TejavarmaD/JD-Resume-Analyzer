import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import {
  AlertTriangle,
  FileSearch,
  LoaderCircle,
  Upload,
} from 'lucide-react'

const API =
  (import.meta as ImportMeta & {
    env?: { VITE_API_URL?: string }
  }).env?.VITE_API_URL || 'http://localhost:8000'

const MAX_RESUME_SIZE = 10 * 1024 * 1024
const MAX_JD_LENGTH = 50_000
const REQUEST_TIMEOUT_MS = 120_000

export type AnalysisResult = {
  run_id: string
  job: {
    title?: string
    [key: string]: unknown
 }
  alignment: {
    alignment_score: number
    interpretation?: string
  }
  summary: {
    total_requirements: number
    matched: number
    partial: number
    missing: number
    must_have_not_fully_matched: number
  }
  category_scores: Record<
    string,
    {
      total_requirements: number
      matched: number
      partial: number
      missing: number
      alignment_score: number
    }
  >
  critical_gaps: Array<{
    requirement_id: string
    requirement: string
    category: string
    status: string
    reason: string
  }>
  experience_eligibility: {
    eligibility_status: string
    reason: string
  }
  requirements: Array<{
    requirement_id: string
    requirement: string
    category: string
    priority: string
    status: string
    status_reason?: string
    evidence_strength?: string
    evidence?: Array<Record<string, unknown>>
  }>
  resume_warnings: Array<{
    type: string
    severity: string
    message: string
    matched_text?: string
    context?: string
    auto_corrected?: boolean
  }>
  limitations: string[]
}

type CandidateAnalyzerProps = {
  onAnalysisStart: () => void
  onResult: (result: AnalysisResult) => void
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isAnalysisResult(value: unknown): value is AnalysisResult {
  if (!isRecord(value)) return false

  const alignment = value.alignment
  const summary = value.summary

  return (
    typeof value.run_id === 'string' &&
    isRecord(value.job) &&
    isRecord(alignment) &&
    typeof alignment.alignment_score === 'number' &&
    Number.isFinite(alignment.alignment_score) &&
    isRecord(summary) &&
    typeof summary.total_requirements === 'number' &&
    typeof summary.matched === 'number' &&
    typeof summary.partial === 'number' &&
    typeof summary.missing === 'number' &&
    Array.isArray(value.requirements) &&
    Array.isArray(value.critical_gaps) &&
    Array.isArray(value.resume_warnings) &&
    Array.isArray(value.limitations) &&
    isRecord(value.category_scores) &&
    isRecord(value.experience_eligibility)
  )
}

async function validateResumeFile(file: File): Promise<string | null> {
  const extension = file.name.split('.').pop()?.toLowerCase()

  if (!extension || !['pdf', 'docx'].includes(extension)) {
    return 'Please upload a PDF or DOCX resume.'
  }

  if (file.size === 0) {
    return 'The selected resume file is empty.'
  }

  if (file.size > MAX_RESUME_SIZE) {
    return 'Resume files must be 10 MB or smaller.'
  }

  const bytes = new Uint8Array(
    await file.slice(0, 8).arrayBuffer()
  )

  if (extension === 'pdf') {
    const signature = new TextDecoder().decode(bytes.slice(0, 5))

    if (signature !== '%PDF-') {
      return 'The selected file does not appear to be a valid PDF.'
    }
  }

  if (extension === 'docx') {
    const isZip =
      bytes.length >= 4 &&
      bytes[0] === 0x50 &&
      bytes[1] === 0x4b &&
      bytes[2] === 0x03 &&
      bytes[3] === 0x04

    if (!isZip) {
      return 'The selected file does not appear to be a valid DOCX.'
    }
  }

  return null
}

async function getApiError(response: Response): Promise<string> {
  const responseText = await response.text()

  if (!responseText) {
    return `The server returned an error (${response.status}).`
  }

  try {
    const payload: unknown = JSON.parse(responseText)

    if (isRecord(payload)) {
      const detail = payload.detail

      if (typeof detail === 'string') {
        return detail
      }

      if (Array.isArray(detail)) {
        return detail
          .map(item => {
            if (!isRecord(item)) return String(item)

            const message =
              typeof item.msg === 'string' ? item.msg : 'Invalid input'

            const location = Array.isArray(item.loc)
              ? item.loc.join(' → ')
              : ''

            return location ? `${location}: ${message}` : message
          })
          .join('; ')
      }
    }
  } catch {
    // The server did not return JSON. Use a safe generic message below.
  }

  return `The server returned an unexpected response (${response.status}).`
}

export default function CandidateAnalyzer({
  onAnalysisStart,
  onResult,
}: CandidateAnalyzerProps) {
  const [resume, setResume] = useState<File | null>(null)
  const [jdText, setJdText] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const requestController = useRef<AbortController | null>(null)
  const requestInProgress = useRef(false)

  useEffect(() => {
    return () => {
      requestController.current?.abort()
    }
  }, [])

  async function analyzeCandidate(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (requestInProgress.current) return

    setError('')

    if (!resume) {
      setError('Please select a PDF or DOCX resume.')
      return
    }

    if (!jdText.trim()) {
      setError('Please enter the job description.')
      return
    }

    if (jdText.length > MAX_JD_LENGTH) {
      setError('Job descriptions must be 50,000 characters or fewer.')
      return
    }

    const fileError = await validateResumeFile(resume)

    if (fileError) {
      setError(fileError)
      return
    }

    const formData = new FormData()
    formData.append('resume', resume)
    formData.append('jd_text', jdText)

    const controller = new AbortController()

    requestController.current = controller
    requestInProgress.current = true

    onAnalysisStart()
    setLoading(true)

    const timeoutId = window.setTimeout(
      () => controller.abort(),
      REQUEST_TIMEOUT_MS
    )

    try {
      const response = await fetch(`${API}/api/candidates/analyze`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(await getApiError(response))
      }

      let payload: unknown

      try {
        payload = await response.json()
      } catch {
        throw new Error(
          'The server returned an invalid response. Please try again.'
        )
      }

      if (!isAnalysisResult(payload)) {
        throw new Error(
          'The server response is missing required analysis data.'
        )
      }

      onResult(payload)
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError(
          'The analysis request timed out or was cancelled. Please try again.'
        )
      } else {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to analyze this candidate.'
        )
      }
    } finally {
      window.clearTimeout(timeoutId)
      requestInProgress.current = false
      requestController.current = null
      setLoading(false)
    }
  }

  return (
    <div className="analyzer-workspace">
      <section className="panel analyzer-form-panel">
        <div className="panel-heading">
          <div>
            <h3>Analyze a candidate</h3>
            <p>
              Upload a resume and provide the job description to evaluate
              documented evidence.
            </p>
          </div>

          <FileSearch size={23} />
        </div>

        <form onSubmit={analyzeCandidate} className="analyzer-form">
          <label htmlFor="candidate-resume">
            Resume (PDF or DOCX)
          </label>

          <input
            id="candidate-resume"
            type="file"
            accept=".pdf,.docx"
            disabled={loading}
            onChange={event => {
              setResume(event.target.files?.[0] || null)
              setError('')
            }}
          />

          {resume && (
            <p className="analyzer-file-name">
              Selected: {resume.name}
            </p>
          )}

          <label htmlFor="candidate-jd">
            Job description
          </label>

          <textarea
            id="candidate-jd"
            rows={12}
            value={jdText}
            disabled={loading}
            maxLength={MAX_JD_LENGTH}
            onChange={event => {
              setJdText(event.target.value)
              setError('')
            }}
            placeholder={`AI Engineer

Must Have:
- Strong Python programming skills
- Experience building REST APIs using FastAPI
- Knowledge of machine learning and PyTorch

Good to Have:
- Experience building AI agents
- Knowledge of cloud platforms`}
          />

          <p className="analyzer-file-name">
            {jdText.length.toLocaleString()} / {MAX_JD_LENGTH.toLocaleString()} characters
          </p>

          {error && (
            <div className="analyzer-error" role="alert">
              <AlertTriangle size={17} />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            className="analyze-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <LoaderCircle size={17} className="spin" />
                Analyzing candidate...
              </>
            ) : (
              <>
                <Upload size={17} />
                Analyze candidate
              </>
            )}
          </button>

          {loading && (
            <p role="status" aria-live="polite">
              Processing the resume and evaluating its evidence against
              the job requirements. This may take a moment.
            </p>
          )}
        </form>
      </section>
    </div>
  )
}