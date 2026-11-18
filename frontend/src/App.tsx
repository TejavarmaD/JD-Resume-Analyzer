import { useState } from 'react'
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  FileSearch,
  LayoutDashboard,
  ShieldCheck,
  Target,
  Upload,
} from 'lucide-react'

import CandidateAnalyzer, {
  type AnalysisResult,
} from './CandidateAnalyzer'

type ResultTab = 'overview' | 'requirements' | 'gaps'

function formatLabel(value: string | null | undefined): string {
  if (typeof value !== 'string' || !value.trim()) {
    return 'Not specified'
  }

  return value.replaceAll('_', ' ')
}

function getEvidenceText(item: Record<string, unknown>): string {
  const fields = [
    'source_text',
    'text',
    'evidence_text',
    'description',
    'matched_text',
  ]

  for (const field of fields) {
    const value = item[field]
    if (typeof value === 'string' && value.trim()) {
      return value.trim()
    }
  }

  return 'No readable evidence quotation is available.'
}

function OverviewTab({ result }: { result: AnalysisResult }) {
  const alignmentScore = Math.max(
    0,
    Math.min(100, Number(result.alignment.alignment_score) || 0)
  )
  return (
    <div className="analyzer-results">
      <section className="panel analyzer-score-panel">
        <div className="panel-heading">
          <div>
            <h3>Candidate overview</h3>
            <p>
              {typeof result.job.title === 'string' && result.job.title.trim()
              ? result.job.title
              : 'Candidate and job description comparison'}
            </p>
          </div>

          <span className="status-pill neutral">
            {formatLabel(
              result.experience_eligibility.eligibility_status
            )}
          </span>
        </div>

                <div className="score-hero">
          <div
            className="score-ring"
            style={{
              background: `conic-gradient(
                var(--color-primary) ${alignmentScore}%,
                rgba(141, 185, 240, 0.18) ${alignmentScore}% 100%
              )`,
            }}
          >
            <div className="score-ring-inner">
              <span className="score-ring-value">
                {alignmentScore.toFixed(2)}%
              </span>
              <span className="score-ring-label">Alignment</span>
            </div>
          </div>

          <div className="score-hero-copy">
            <h3>Weighted evidence alignment</h3>
            <p>
              Measures how strongly the resume supports the requirements
              identified in the job description.
            </p>
            <span className="score-context">
              Based on documented evidence, not hiring probability
            </span>
          </div>
        </div>

        <div className="analyzer-summary-grid">
          <div>
            <b>{result.summary.total_requirements}</b>
            <span>Total</span>
          </div>
          <div>
            <b>{result.summary.matched}</b>
            <span>Matched</span>
          </div>
          <div>
            <b>{result.summary.partial}</b>
            <span>Partial</span>
          </div>
          <div>
            <b>{result.summary.missing}</b>
            <span>Missing</span>
          </div>
        </div>
      </section>

      <section className="panel category-panel">
        <div className="panel-heading">
          <div>
            <h3>Alignment by category</h3>
            <p>Evidence coverage across job requirement categories</p>
          </div>
        </div>

        <div className="category-list">
          {Object.entries(result.category_scores).map(
            ([name, item]) => (
              <div className="category-row" key={name}>
                <div className="category-name">
                  {formatLabel(name)}
                </div>

                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${Math.max(
                        0,
                        Math.min(100, item.alignment_score)
                      )}%`,
                    }}
                  />
                </div>

                <div className="category-score">
                  {item.alignment_score.toFixed(1)}%
                </div>

                <div className="category-count">
                  {item.total_requirements} req.
                </div>
              </div>
            )
          )}
        </div>
      </section>

      <section className="panel eligibility-card">
        <div className="panel-heading">
          <div>
            <h3>Experience eligibility</h3>
            <p>Independent verification of experience requirements</p>
          </div>

          <div className="eligibility-icon">
            <ShieldCheck size={21} />
          </div>
        </div>

        <div className="eligibility-status-row">
          <span className="eligibility-status-label">
            Verification status
          </span>

          <span className="eligibility-status-value">
            {formatLabel(
              result.experience_eligibility.eligibility_status
            )}
          </span>
        </div>

        <div className="eligibility-explanation">
          <span className="eligibility-explanation-title">
            Assessment details
          </span>

          <p>
            {result.experience_eligibility.reason ||
              'No additional eligibility explanation was provided.'}
          </p>
        </div>

        <div className="eligibility-disclaimer">
          <ShieldCheck size={15} />
          <span>
            Evidence alignment and experience eligibility are assessed
            separately. An unverified status does not mean ineligible.
          </span>
        </div>
      </section>


      {result.resume_warnings.length > 0 && (
        <section className="panel resume-warnings-panel">
          <div className="panel-heading">
            <div>
              <h3>Resume review warnings</h3>
              <p>
                Issues identified during resume extraction and review
              </p>
            </div>

            <div className="warning-count">
              {result.resume_warnings.length}{" "}
              {result.resume_warnings.length === 1 ? "warning" : "warnings"}
            </div>
          </div>

          <div className="warning-list">
            {result.resume_warnings.map((warning, index) => (
              <article
                className="warning-card"
                key={`${warning.type}-${index}`}
              >
                <div className="warning-card-header">
                  <div className="warning-type">
                    <AlertTriangle size={17} />
                    <strong>{formatLabel(warning.type)}</strong>
                  </div>

                  <span
                    className={`warning-severity severity-${warning.severity.toLowerCase()}`}
                  >
                    {formatLabel(warning.severity)}
                  </span>
                </div>

                <p className="warning-message">{warning.message}</p>

                {warning.matched_text && (
                  <div className="warning-detail">
                    <span className="warning-detail-label">
                      Matched resume text
                    </span>
                    <p>{warning.matched_text}</p>
                  </div>
                )}

                {warning.context && (
                  <div className="warning-detail">
                    <span className="warning-detail-label">
                      Additional context
                    </span>
                    <p>{warning.context}</p>
                  </div>
                )}

                {warning.auto_corrected && (
                  <span className="warning-corrected">
                    Automatically corrected
                  </span>
                )}
              </article>
            ))}
          </div>
        </section>
      )}


      {result.limitations.length > 0 && (
        <section className="panel scoring-limitations-panel">
          <div className="panel-heading">
            <div>
              <h3>Scoring limitations</h3>
              <p>
                Important constraints to consider when interpreting this analysis
              </p>
            </div>

            <div className="limitations-icon">
              <AlertTriangle size={19} />
            </div>
          </div>

          <div className="limitations-list">
            {result.limitations.map((item, index) => (
              <div
              className="limitation-item"
              key={`${index}-${item.slice(0, 40)}`}
            >

              <span className="limitation-number">
                {String(index + 1).padStart(2, '0')}
              </span>

              <p>{item}</p>
            </div>
          ))}
        </div>

        <div className="limitations-note">
          <ShieldCheck size={16} />
          <span>
            These limitations should be considered before drawing conclusions
            from the alignment score or candidate assessment.
          </span>
        </div>
      </section>
    )}

      <section className="panel analyzer-integrity">
        <CheckCircle2 size={18} />
        <div>
          <b>Analysis completed successfully</b>
          <p>Run ID: {result.run_id}</p>
          <p>
            Scores reflect documented evidence, not candidate ability
            or hiring probability.
          </p>
        </div>
      </section>
    </div>
  )
}

function RequirementsTab({ result }: { result: AnalysisResult }) {
  const { summary } = result

  return (
    <section className="panel explorer requirements-panel">
      <div className="panel-heading">
        <div>
          <h3>Requirement assessment</h3>
          <p>
            Review every job requirement, its match status, and the
            supporting resume evidence.
          </p>
        </div>
        <span className="subtle-tag">
          {summary.total_requirements} total requirements
        </span>
      </div>

      <div className="requirements-summary">
        <div>
          <b>{summary.matched}</b>
          <span>Matched</span>
        </div>
        <div>
          <b>{summary.partial}</b>
          <span>Partially matched</span>
        </div>
        <div>
          <b>{summary.missing}</b>
          <span>Missing</span>
        </div>
      </div>

      {result.requirements.length > 0 ? (
        <div className="requirements-list">
          {result.requirements.map(item => (
            <article
              className="candidate-requirement requirement-card"
              key={item.requirement_id}
            >
              <div className="requirement-card-content">
                <div className="requirement-card-heading">
                  <span className="requirement-id">
                    {item.requirement_id}
                  </span>
                  <span className={`status-pill ${item.status}`}>
                    {formatLabel(item.status)}
                  </span>
                </div>

                <h4>{item.requirement}</h4>

                <div className="requirement-meta">
                  <span>{formatLabel(item.category)}</span>
                  <span>{formatLabel(item.priority)} priority</span>
                  <span>
                    Evidence: {formatLabel(item.evidence_strength)}
                  </span>
                </div>

                {item.status_reason && (
                  <div className="requirement-reason">
                    <b>Assessment explanation</b>
                    <p>{item.status_reason}</p>
                  </div>
                )}

                {item.evidence && item.evidence.length > 0 && (
                  <div className="requirement-evidence">
                    <div className="evidence-section-heading">
                      <b>Supporting evidence</b>
                      <span>
                        {item.evidence.length}{' '}
                        {item.evidence.length === 1 ? 'excerpt' : 'excerpts'}
                      </span>
                    </div>

                    {item.evidence.map((evidence, index) => (
                      <div
                        className="evidence-card"
                        key={`${item.requirement_id}-evidence-${index}`}
                      >
                        <div className="evidence-card-header">
                          <span className="evidence-tag">
                            Resume evidence
                          </span>
                          <span className="evidence-index">
                            Excerpt {index + 1}
                          </span>
                        </div>
                        <p>{getEvidenceText(evidence)}</p>
                      </div>
                    ))}
                  </div>
                )}

                {(!item.evidence || item.evidence.length === 0) && (
                  <div className="no-evidence-note">
                    No supporting resume evidence was returned for this
                    requirement.
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="requirements-empty">
          <FileSearch size={27} />
          <b>No requirements available</b>
          <p>
            The analysis did not return individual requirement assessments.
          </p>
        </div>
      )}
    </section>
  )
}

function GapsTab({ result }: { result: AnalysisResult }) {
  return (
    <section className="panel explorer gaps-panel">
      <div className="panel-heading">
        <div>
          <h3>Critical evidence gaps</h3>
          <p>
            Must-have requirements that are not fully supported by the
            available resume evidence.
          </p>
        </div>

        <span className="status-pill warning">
          {result.critical_gaps.length}{' '}
          {result.critical_gaps.length === 1 ? 'gap' : 'gaps'}
        </span>
      </div>

      {result.critical_gaps.length > 0 ? (
        <div className="gaps-list">
          {result.critical_gaps.map(gap => (
            <article
              className="candidate-gap gap-card"
              key={gap.requirement_id}
            >
              <div className="gap-card-icon">
                <AlertTriangle size={19} />
              </div>

              <div className="gap-card-content">
                <div className="gap-card-heading">
                  <span className="requirement-id">
                    {gap.requirement_id}
                  </span>

                  <span className={`status-pill ${gap.status}`}>
                    {formatLabel(gap.status)}
                  </span>
                </div>

                <h4>{gap.requirement}</h4>

                <span className="gap-category">
                  {formatLabel(gap.category)}
                </span>

                <div className="gap-reason">
                  <b>Why this is flagged</b>
                  <p>{gap.reason}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="gaps-empty">
          <CheckCircle2 size={30} />
          <b>No critical evidence gaps identified</b>
          <p>
            The analysis did not flag any critical gaps in the returned
            assessment.
          </p>
          <small>
            This does not independently verify every qualification or
            guarantee job eligibility.
          </small>
        </div>
      )}
    </section>
  )
}

export default function App() {
  const [candidateResult, setCandidateResult] =
    useState<AnalysisResult | null>(null)

  const [active, setActive] = useState<'analyze' | 'results'>(
    'analyze'
  )

  const [resultTab, setResultTab] =
    useState<ResultTab>('overview')

  function handleAnalysisResult(result: AnalysisResult) {
    setCandidateResult(result)
    setResultTab('overview')
    setActive('results')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Target size={20} />
          </div>

          <div>
            <strong>EvidenceFirst</strong>
            <span>JD–Resume Analyzer</span>
          </div>
        </div>

        <div className="side-label">WORKSPACE</div>

        <button
          className={
            active === 'analyze' ? 'nav-item active' : 'nav-item'
          }
          onClick={() => setActive('analyze')}
        >
          <Upload size={17} />
          Analyze Candidate
        </button>

        <button
          className={
            active === 'results' ? 'nav-item active' : 'nav-item'
          }
          onClick={() => {
            if (candidateResult) {
              setActive('results')
            }
          }}
          disabled={!candidateResult}
        >
          <FileSearch size={17} />
          Analysis Results

          {candidateResult && (
            <span className="nav-count">1</span>
          )}
        </button>

        <div className="sidebar-bottom">
          <ShieldCheck size={17} />
          <div>
            <b>Evidence-first scoring</b>
            <span>Transparent rules. No invented claims.</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">
              ANALYSIS WORKSPACE / RESUME REVIEW
            </div>

            <h1>
              {active === 'analyze'
                ? 'Analyze Candidate'
                : 'Analysis Results'}
            </h1>
          </div>

          <div className="top-meta">
            <span className="live-dot" />
            API analysis
          </div>
        </header>

        {active === 'analyze' && (
          <CandidateAnalyzer
          onAnalysisStart={() => {
            setCandidateResult(null)
            setResultTab('overview')
            setActive('analyze')
          }}
          onResult={handleAnalysisResult}
        />
        )}

        {active === 'results' && candidateResult && (
          <div className="results-workspace">
            <div className="results-toolbar">
              <button
                className="text-button"
                onClick={() => setActive('analyze')}
              >
                <ArrowLeft size={16} />
                Back to Analyze Candidate
              </button>

              <span className="subtle-tag">
                Run: {candidateResult.run_id.slice(0, 8)}
              </span>
            </div>

            <div className="results-tabs" role="tablist">
              <button
                className={
                  resultTab === 'overview'
                    ? 'results-tab active'
                    : 'results-tab'
                }
                onClick={() => setResultTab('overview')}
                role="tab"
                aria-selected={resultTab === 'overview'}
              >
                <LayoutDashboard size={16} />
                Overview
              </button>

              <button
                className={
                  resultTab === 'requirements'
                    ? 'results-tab active'
                    : 'results-tab'
                }
                onClick={() => setResultTab('requirements')}
                role="tab"
                aria-selected={resultTab === 'requirements'}
              >
                <FileSearch size={16} />
                Requirements ({candidateResult.requirements.length})
              </button>

              <button
                className={
                  resultTab === 'gaps'
                    ? 'results-tab active'
                    : 'results-tab'
                }
                onClick={() => setResultTab('gaps')}
                role="tab"
                aria-selected={resultTab === 'gaps'}
              >
                <AlertTriangle size={16} />
                Critical Gaps ({candidateResult.critical_gaps.length})
              </button>
            </div>

            {resultTab === 'overview' && (
              <OverviewTab result={candidateResult} />
            )}

            {resultTab === 'requirements' && (
              <RequirementsTab result={candidateResult} />
            )}

            {resultTab === 'gaps' && (
              <GapsTab result={candidateResult} />
            )}
          </div>
        )}

        <footer className="footer-note">
          <span>EvidenceFirst · Evidence-based analysis</span>
          <span>
            Scores reflect documented evidence, not candidate ability
            or hiring probability.
          </span>
        </footer>
      </main>
    </div>
  )
}
