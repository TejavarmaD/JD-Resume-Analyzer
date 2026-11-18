# EvidenceFirst --- Role-Agnostic JD--Resume Analyzer

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Status](https://img.shields.io/badge/Status-Development%20%2F%20Deployment%20Pending-orange)](#release-and-deployment-status)

**EvidenceFirst** is a role-agnostic job-description and resume analysis
application. It extracts requirements from a job description (JD),
evaluates the evidence available in an uploaded resume, and presents
requirement-level results with traceable explanations.

The project is designed around one principle:

> A match should be supported by evidence in the resume---not inferred
> from a keyword alone.

The application combines a deterministic Python analysis pipeline with a
React + TypeScript interface and a FastAPI service. It is intended to
help candidates understand where their experience aligns with a role,
where evidence is incomplete, and where a requirement is not
demonstrated by the submitted resume.

------------------------------------------------------------------------

## Table of contents

-   [At a glance](#at-a-glance)
-   [Why this project exists](#why-this-project-exists)
-   [Project evolution](#project-evolution)
-   [What the application does](#what-the-application-does)
-   [How the analysis works](#how-the-analysis-works)
-   [Evidence and matching
    methodology](#evidence-and-matching-methodology)
-   [System architecture](#system-architecture)
-   [Technology stack](#technology-stack)
-   [Quantitative development and validation
    results](#quantitative-development-and-validation-results)
-   [Illustrative analysis example](#illustrative-analysis-example)
-   [API overview](#api-overview)
-   [Repository structure](#repository-structure)
-   [Run locally](#run-locally)
-   [Configuration and limits](#configuration-and-limits)
-   [Privacy and data handling](#privacy-and-data-handling)
-   [Known limitations](#known-limitations)
-   [Roadmap](#roadmap)
-   [Release and deployment status](#release-and-deployment-status)
-   [Engineering principles](#engineering-principles)

------------------------------------------------------------------------

## At a glance

  -----------------------------------------------------------------------------------------------------------------------
  Area                                Current implementation
  ----------------------------------- -----------------------------------------------------------------------------------
  Product                             EvidenceFirst --- JD--Resume Analyzer

  Core purpose                        Analyze a resume against a supplied job description

  Role support                        Role-agnostic; driven by the supplied JD rather than one hardcoded job title

  Analysis engine                     Deterministic Python extraction, classification and evidence-matching pipeline

  Resume formats                      PDF and DOCX

  JD input                            Pasted job-description text

  Backend                             FastAPI

  Frontend                            React + TypeScript + Vite

  Result granularity                  Individual requirements, evidence status and overall alignment summary

  Evidence states                     Matched, partial and missing; evidence provenance is retained by the analysis
                                      pipeline

  Resume upload limit                 10 MB

  JD text limit                       50,000 characters

  Automated validation                Python test suite; frontend production build

  Repository                          [TejavarmaD/JD-Resume-Analyzer](https://github.com/TejavarmaD/JD-Resume-Analyzer)

  Current Git release commit          `05c3d3c` --- `Build role-agnostic JD resume analysis web app`

  Deployment                          Not yet deployed; Render + Vercel are the planned hosting approach
  -----------------------------------------------------------------------------------------------------------------------

The status and test figures in this document refer to the repository
state at the release commit identified above. They should not be
interpreted as a claim that a public production deployment is live.

------------------------------------------------------------------------

## Why this project exists

A conventional resume-to-job-description comparison can be misleading
when it relies mainly on keyword overlap. A resume may mention a
technology without showing how it was used; conversely, a candidate may
demonstrate a capability through project outcomes without using the
exact wording found in the JD.

EvidenceFirst was developed to make that comparison more transparent.

The system aims to answer five practical questions:

1.  **What is the employer asking for?** Extract individual requirements
    from the JD, including responsibilities, qualifications and
    technical skills.
2.  **What does the resume actually demonstrate?** Locate relevant
    statements and associate them with requirements.
3.  **How strong is the evidence?** Separate direct evidence from
    incomplete or absent evidence.
4.  **Where are the gaps?** Make missing and partially supported
    requirements visible.
5.  **What should the candidate investigate or improve?** Provide a
    structured basis for reviewing the resume and preparing for an
    application.

The tool is an analysis aid, not a hiring decision system. Its output
should support human review rather than replace it.

------------------------------------------------------------------------

## Project evolution

The project evolved through multiple development iterations, from a
local Python analysis workflow to a web application. The following is a
condensed engineering history of the work carried through the Resume
Analyzer Plan development series.

### Phase 1 --- Establishing the analysis foundation

The initial work focused on extracting resume content and comparing it
with job-description requirements. A deterministic baseline was selected
so that results could be inspected, tested and reproduced without
depending on a language-model response.

Early development concentrated on: - Parsing resume content from PDF and
DOCX documents. - Extracting requirements from job descriptions. -
Matching requirement language against resume evidence. - Producing
requirement-level statuses. - Creating a repeatable test suite before
expanding the application.

An early baseline reached **85 passing tests**. This was an intermediate
milestone, not the final release test count.

### Phase 2 --- Requirement extraction and classification

Testing exposed a key weakness in the original JD extraction approach:
it relied too heavily on list markers. A JD can express requirements as
standalone paragraphs, nested sections, numbered statements or inline
qualification fields. Ignoring non-bullet text can silently remove
important requirements from the analysis.

The parser was therefore expanded and tested to support more varied JD
structures, including: - Bullet and numbered requirements. - Standalone
requirement paragraphs. - Nested headings and section context. -
Required and preferred qualifications. - Technical-stack summaries. -
Responsibilities and role-context sections.

The goal was to improve the extraction architecture generically---not to
patch the parser for one specific job description.

### Phase 3 --- Moving toward role-agnostic evaluation

The product requirement became explicit: the analyzer must work with
different roles and industries, not only AI Engineering.

The analysis pipeline was shaped around the supplied JD. Requirement
categories and evidence evaluation should follow the content of the job
description rather than assume a fixed job family.

The generic evaluation path was developed alongside regression coverage
for earlier behavior. This helped preserve compatibility while shifting
live evaluation toward more general requirement and evidence matching.

### Phase 4 --- Evidence quality and manual confirmation

A keyword hit is not necessarily proof that a candidate performed a
task. The matcher was refined to distinguish lexical relevance from
stronger implementation evidence.

The evidence workflow includes: - Resume-derived evidence. -
Requirement-level evidence groups. - Source text and section context. -
Evidence status and explanation. - Manual confirmation where a candidate
can clarify experience not explicitly stated in the resume.

Manual confirmation is treated as a separate evidence input. A manually
marked missing item must not accidentally become satisfied merely
because it belongs to a single evidence group. Regression tests were
added for this behavior.

### Phase 5 --- Structured analysis and scoring

The project added separate modules for requirement extraction, skill
tagging, structured entities, matching scores and evidence status. This
separation makes the pipeline easier to test and maintain.

The resulting design keeps the underlying requirement evaluations
available instead of reducing the analysis to a single opaque score.

### Phase 6 --- Web application

The user interface direction moved from an early lightweight UI approach
to **React + TypeScript + Vite**, with **FastAPI** providing the
backend.

The web application introduced: - A dashboard-oriented interface. -
Resume and JD submission. - API-backed candidate analysis. -
Requirement-level result views. - Backend health and analysis
endpoints. - Environment-based frontend/backend configuration.

### Phase 7 --- Release candidate, repository cleanup and publication

The release candidate was consolidated into a single repository. Private
resume files, local analysis outputs, caches, dependency directories and
temporary artifacts were excluded from Git.

The combined release candidate was validated with Python tests and a
Vite production build. The code was committed and pushed to the `main`
branch.

**Published release commit:** `05c3d3c`\
**Commit message:** `Build role-agnostic JD resume analysis web app`\
**Repository:**
[GitHub](https://github.com/TejavarmaD/JD-Resume-Analyzer)

------------------------------------------------------------------------

## What the application does

### 1. Resume ingestion

-   Accepts PDF and DOCX resumes.
-   Extracts document text for downstream analysis.
-   Uses the extracted content as the evidence source for requirement
    matching.
-   Applies a maximum resume upload size of 10 MB.

### 2. Job-description ingestion

-   Accepts pasted JD text.
-   Extracts requirements from multiple structural formats.
-   Retains section context to help interpret the type and priority of a
    requirement.
-   Applies a maximum JD text length of 50,000 characters.

### 3. Requirement extraction and classification

The JD is converted into a structured set of requirements. Depending on
the source JD, these can include: - Responsibilities and role
expectations. - Required qualifications. - Preferred qualifications. -
Technical skills and technology-stack expectations. - Professional and
behavioral capabilities. - General role requirements.

The exact set of categories is driven by the JD content. A fixed
category distribution is not imposed on every role.

### 4. Resume evidence matching

Each extracted requirement is evaluated against the resume. The engine
looks for relevant evidence and differentiates between: - Direct or
strong supporting evidence. - Partial or incomplete evidence. - No
adequate evidence found.

The analysis preserves requirement-level results so that a user can
inspect why a requirement received a particular status.

### 5. Evidence status and alignment summary

The system presents an overall summary alongside individual requirement
evaluations. The summary is intended to make the result easier to scan;
the requirement-level evidence remains the more important basis for
interpretation.

### 6. Candidate analysis API

The FastAPI backend exposes endpoints for health checks, dashboard
information, requirement results and candidate analysis.

------------------------------------------------------------------------

## How the analysis works

The current pipeline is deterministic and rule-based. It does not
require a generative model to decide whether a resume satisfies a
requirement.

At a high level:

``` text
Job Description
      |
      v
JD text normalization
      |
      v
Requirement extraction
      |
      v
Requirement classification / skill tagging
      |
      +----------------------------------+
                                         |
Resume PDF / DOCX                        |
      |                                  |
      v                                  |
Document text extraction                 |
      |                                  |
      v                                  |
Resume structure and evidence extraction|
      |                                  |
      +----------------+-----------------+
                       |
                       v
           Requirement-to-evidence evaluation
                       |
                       v
              Evidence status assignment
                       |
                       v
              Matching score calculation
                       |
                       v
             API response / React UI
```

### Pipeline stages

  -----------------------------------------------------------------------
  Stage                   Responsibility          Typical output
  ----------------------- ----------------------- -----------------------
  Document extraction     Read text from PDF/DOCX Extracted resume text

  JD parsing              Identify requirement    Structured JD
                          statements and context  requirements

  Classification          Determine requirement   Requirement metadata
                          type and relevant tags  

  Resume parsing          Identify sections and   Resume evidence records
                          structured entities     

  Evidence matching       Compare requirements    Matched / partial /
                          with resume evidence    missing evaluation

  Evidence status         Normalize and explain   Evidence status record
                          evidence state          

  Scoring                 Aggregate               Alignment summary
                          requirement-level       
                          outcomes                

  API/UI                  Deliver results to the  Dashboard and detailed
                          application             results
  -----------------------------------------------------------------------

The stages are separated so that extraction, classification, evidence
evaluation and scoring can be tested independently.

------------------------------------------------------------------------

## Evidence and matching methodology

### Evidence-first rather than keyword-first

A shared word or technology name can indicate relevance, but it does not
automatically prove that a candidate has the required experience.

For example: - A resume that lists "Python" may show exposure to the
language. - A project bullet describing a Python data pipeline, its
inputs and its outcome provides stronger evidence of applied
experience. - A requirement asking for production deployment should not
be considered fully demonstrated by a resume that only mentions
experimentation.

The matcher therefore distinguishes keyword relevance from evidence that
supports the actual requirement.

### Result statuses

  -----------------------------------------------------------------------
  Status                              Meaning
  ----------------------------------- -----------------------------------
  **Matched**                         The available resume evidence
                                      sufficiently supports the
                                      requirement under the current
                                      deterministic rules.

  **Partial**                         Some relevant evidence exists, but
                                      the full requirement is not clearly
                                      demonstrated.

  **Missing**                         The analysis did not find
                                      sufficient resume evidence for the
                                      requirement. This does not prove
                                      the candidate lacks the skill; it
                                      means the submitted resume does not
                                      establish it.
  -----------------------------------------------------------------------

### Manual evidence

A candidate may know that they performed work that is not clearly
described in their resume. The manual-evidence mechanism allows
additional confirmation to be represented separately from resume-derived
evidence.

This distinction matters: - Resume evidence describes what the submitted
document demonstrates. - Manual evidence records a candidate-provided
clarification. - The final evaluation should not misrepresent manual
confirmation as text found in the resume.

### Scoring interpretation

An alignment score is a summary generated by the scoring engine. It is
not: - A probability of getting an interview. - A prediction of
recruiter behavior. - A validated measure of job performance. - A
universal score that can be compared across unrelated JDs without
context.

A low score can indicate missing evidence in the document, not
necessarily a lack of underlying ability. A high score does not
guarantee that the candidate meets every hiring criterion.

------------------------------------------------------------------------

## System architecture

The application is divided into three main layers.

### Frontend

**React + TypeScript + Vite**

The frontend is responsible for: - The dashboard and application
layout. - Resume and JD input. - Calling the backend analysis API. -
Displaying candidate analysis and requirement-level outcomes. -
Presenting loading and error states.

### Backend

**FastAPI**

The backend is responsible for: - HTTP API endpoints. - Input validation
and upload limits. - Orchestrating the candidate analysis pipeline. -
Returning structured analysis results. - Configuring permitted frontend
origins through CORS.

### Analysis engine

**Python**

The analysis engine contains the deterministic logic for: - JD
extraction and classification. - Resume extraction and parsing. -
Skill-tag extraction. - Requirement-to-evidence matching. - Evidence
status evaluation. - Matching-score calculation. - Experience
eligibility evaluation.

The backend orchestrates these modules; it should not duplicate the
analysis rules in the frontend.

------------------------------------------------------------------------

## Technology stack

  Layer                         Technologies
  ----------------------------- --------------------------------------------
  Programming language          Python
  API framework                 FastAPI
  ASGI server                   Uvicorn
  Frontend framework            React
  Frontend language             TypeScript
  Frontend build tool           Vite
  Styling                       CSS
  Document formats              PDF, DOCX
  Data processing               Python parsing and structured data modules
  Testing                       pytest
  Frontend package management   npm
  Version control               Git and GitHub
  Planned backend hosting       Render
  Planned frontend hosting      Vercel

The analysis engine is deterministic. The current release should not be
described as a fine-tuned AI model, an LLM-powered evaluator or a
machine-learning classifier. Those would imply capabilities that are not
part of the verified implementation.

------------------------------------------------------------------------

## Quantitative development and validation results

This section deliberately separates **verified engineering
measurements** from example analysis outputs and historical milestones.

### Release-candidate validation

The final matcher correction was followed by a full Python test run
with:

  Metric                         Result
  ------------------ ------------------
  Tests passed                  **134**
  Tests skipped                  **21**
  Subtests passed                **37**
  Test failures                   **0**
  Warnings                        **1**
  Recorded runtime     **2.92 seconds**

The warning was a Starlette deprecation warning concerning the use of
`httpx` with `starlette.testclient`. It did not cause test failures.

Earlier combined release-candidate validation recorded **133 passed, 21
skipped, 37 subtests**, and the matcher regression fix increased the
passing count to **134**.

### Earlier testing milestones

The development process used progressively broader test coverage.
Historical milestones included:

  ------------------------------------------------------------------------
  Development milestone                Passing tests Additional detail
  --------------------- ---------------------------- ---------------------
  Initial baseline                                85 Early deterministic
                                                     analysis foundation

  Generic evaluator                              112 45 subtests; 1
  milestone                                          deprecation warning

  Intermediate                                   131 Historical suite
  expansion                                          milestone

  Broader development                            151 49 subtests;
  validation                                         historical milestone

  Combined web-app                               133 21 skipped; 37
  release candidate                                  subtests

  Latest recorded                            **134** **21 skipped; 37
  release-candidate run                              subtests; 0
                                                     failures**
  ------------------------------------------------------------------------

These are results from different development snapshots and test-suite
compositions. They should not be added together or interpreted as 151 +
134 unique tests. The latest release-candidate result is the most
relevant figure for the published code snapshot.

### Frontend build validation

  Metric                                                 Result
  --------------------------------------------- ---------------
  Build tool                                         Vite 6.4.5
  Modules transformed                                 **1,578**
  JavaScript bundle (reported build size)         **167.28 kB**
  CSS bundle (reported build size)                 **36.92 kB**
  Production build                                   **Passed**
  npm packages installed during clean install            **72**

The bundle figures are the build output reported at the time of
validation; they are not runtime performance or page-load benchmarks.

### Repository and release measurements

  Metric                                                      Result
  ----------------------------------------------------- ------------
  Files in release commit                                     **46**
  Insertions in release commit                            **12,671**
  Deletions in release commit                                 **45**
  Files copied during release-candidate consolidation         **59**
  Copy failures reported                                       **0**
  Release commit                                           `05c3d3c`
  Branch pushed                                               `main`

The Git commit statistics describe the committed source change, not the
total number of lines in the complete repository.

### Input constraints

  Input                             Configured limit
  -------------------------- -----------------------
  Resume file                              **10 MB**
  Pasted job description       **50,000 characters**
  Supported resume formats       **2: PDF and DOCX**

### What these numbers do---and do not---measure

The test counts measure automated test outcomes. The build metrics
measure a successful frontend compilation. The Git metrics measure the
published source change.

They do **not** establish: - Resume parsing accuracy across a
representative external dataset. - Precision, recall, F1 score or
false-positive rate. - Agreement with professional recruiters. -
Reduction in job-search time. - Improvement in interview conversion. -
Production uptime, latency or concurrent-user capacity.

Those outcomes require a separately designed evaluation and real-world
measurement.

------------------------------------------------------------------------

## Illustrative analysis example

The following is a historical development example using a Generative AI
Engineer job description. It demonstrates how requirement-level outputs
can be summarized. It is **not** a benchmark of the product across all
roles.

### Earlier 68-requirement snapshot

One historical analysis contained: - **68** extracted requirements. -
**7** matched. - **16** partial. - **45** missing. - **54** identified
as critical gaps. - A reported alignment score of **21.41%**.

The status counts sum to 68: 7 + 16 + 45 = 68.

### Later 68-requirement matcher snapshot

After subsequent matcher changes, a later analysis of the same example
resume/JD set reported: - **68** requirements. - **11** matched. -
**11** partial. - **46** missing.

The status counts sum to 68: 11 + 11 + 46 = 68.

This later output is a different analysis snapshot. It should not be
mixed with the earlier 21.41% score as though they were generated by one
unchanged scoring configuration.

### A separate 72-requirement extraction snapshot

A previous extraction/classification review produced **72** requirements
for an AI Engineer example JD. The category distribution at that point
was:

  Category                 Requirements
  ---------------------- --------------
  Generative AI / LLM                15
  Agentic Systems                    10
  Retrieval                           9
  Evaluation                          8
  Professional Skills                 6
  Software Engineering                6
  Cloud / DevOps                      6
  Security                            3
  Qualifications                      2
  Data Analytics                      1
  AI                                  1
  General                             5
  **Total**                      **72**

These category counts describe that particular JD extraction snapshot
only. They are not a fixed taxonomy or expected distribution for every
job description. The 72-requirement extraction and 68-requirement
matcher examples are separate snapshots and should not be treated as the
same run.

------------------------------------------------------------------------

## API overview

The FastAPI application currently defines the following routes:

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Purpose
  ----------------------- -------------------------------------- -----------------------
  `GET`                   `/api/health`                          Backend health check

  `GET`                   `/api/dashboard`                       Dashboard summary

  `GET`                   `/api/requirements`                    Requirement results

  `GET`                   `/api/requirements/{requirement_id}`   Details for one
                                                                 requirement

  `POST`                  `/api/candidates/analyze`              Analyze an uploaded
                                                                 resume against JD text
  --------------------------------------------------------------------------------------

The interactive API documentation is available at `/docs` when the
backend is running locally.

### Example local endpoints

-   Frontend: `http://localhost:5173`
-   Backend: `http://localhost:8000`
-   Health: `http://localhost:8000/api/health`
-   API docs: `http://localhost:8000/docs`

The frontend API base URL is configurable through `VITE_API_URL`. Do not
append `/api` to the configured base URL.

------------------------------------------------------------------------

## Repository structure

``` text
JD-Resume-Analyzer/
|
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- candidate_pipeline.py
|   |   `-- main.py
|   |-- requirements.txt
|   `-- README.md
|
|-- frontend/
|   |-- src/
|   |   |-- App.tsx
|   |   |-- CandidateAnalyzer.tsx
|   |   |-- main.tsx
|   |   `-- styles.css
|   |-- index.html
|   |-- package.json
|   |-- package-lock.json
|   |-- tsconfig.json
|   |-- vite.config.ts
|   `-- .env.example
|
|-- docs/
|   `-- ENGINEERING_NOTES.md
|
|-- evidence_status_engine.py
|-- experience_eligibility.py
|-- extract_documents.py
|-- jd_analyzer.py
|-- matching_score_engine.py
|-- resume_evidence_matcher.py
|-- skill_tag_dictionary.py
|-- skill_tag_extractor.py
|-- structured_entity_extractor.py
|-- structured_resume_parser.py
|
|-- test_candidate_api.py
|-- test_candidate_pipeline.py
|-- test_evidence_status_engine.py
|-- test_generic_requirement_evaluator.py
|-- test_jd_extraction_formats.py
|-- test_jd_requirement_classification.py
|-- test_matching_score_engine.py
|-- test_resume_evidence_matcher.py
|-- test_role_agnostic_categories.py
|-- test_role_agnostic_extraction.py
|-- test_skill_tag_extractor.py
|-- test_skill_tag_schema.py
|-- test_structured_entities.py
|-- test_structured_parser.py
|
|-- requirements.txt
|-- requirements-dev.txt
|-- pytest.ini
|-- .env.example
|-- .gitignore
|-- README.md
`-- README_WEB_APP.md
```

The tree is representative of the release repository. It omits generated
caches, installed dependencies, local candidate runs, private input
documents and other ignored working files.

------------------------------------------------------------------------

## Run locally

### Prerequisites

Install: - Python 3.12 or a compatible supported Python version. -
Node.js and npm. - Git.

Clone the repository:

``` bash
git clone https://github.com/TejavarmaD/JD-Resume-Analyzer.git
cd JD-Resume-Analyzer
```

### 1. Set up the Python environment

Windows PowerShell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

If PowerShell blocks virtual-environment activation, use the appropriate
execution-policy setting for your environment or invoke the virtual
environment's Python executable directly.

### 2. Configure the backend

Copy the example environment file:

``` powershell
Copy-Item .env.example .env
```

The example contains local CORS origins. Adjust `CORS_ORIGINS` for the
frontend origin you intend to use. Keep real secrets and private
configuration out of Git.

### 3. Start the backend

From the repository root:

``` powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Check: - `http://localhost:8000/api/health` -
`http://localhost:8000/docs`

### 4. Install and start the frontend

Open a second terminal:

``` powershell
cd frontend
npm ci
```

Create the frontend environment file:

``` powershell
Copy-Item .env.example .env
```

For local development, the example points to:

``` env
VITE_API_URL=http://localhost:8000
```

Start Vite:

``` powershell
npm run dev
```

Open `http://localhost:5173`.

### 5. Run the tests

From the repository root with the Python environment active:

``` powershell
python -m pytest -q
```

### 6. Build the frontend

From the `frontend` directory:

``` powershell
npm run build
```

------------------------------------------------------------------------

## Configuration and limits

### Backend environment

Example root `.env.example`:

``` env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`CORS_ORIGINS` is a comma-separated list of exact frontend origins
permitted to call the backend.

### Frontend environment

Example `frontend/.env.example`:

``` env
VITE_API_URL=http://localhost:8000
```

This is the backend base URL. The frontend/API integration handles the
API path; do not set this value to a URL that already ends in `/api`.

### Upload and text limits

-   Resume upload: 10 MB maximum.
-   JD text: 50,000 characters maximum.
-   Resume formats: PDF and DOCX.

These are application-level limits, not claims about the maximum
capabilities of the underlying file formats.

------------------------------------------------------------------------

## Privacy and data handling

The repository's ignore rules are intended to prevent personal candidate
documents and local analysis artifacts from being committed.

Examples of excluded content include: - PDF and DOCX files. - Local JD
input and result directories. - Candidate run outputs. - Extraction and
structured-result directories. - Python caches and test caches. -
Virtual environments. - Node dependencies and build output. - Local
environment files. - Temporary backups and editor artifacts.

The published source repository does not include the developer's private
resume documents or private candidate-analysis outputs.

Before deploying or using the application with real candidate data,
review the hosting configuration, retention behavior, access controls,
logging and applicable privacy requirements. Do not upload sensitive
personal documents to an environment unless its data-handling practices
are understood.

------------------------------------------------------------------------

## Known limitations

EvidenceFirst is an evolving analysis tool. The following limitations
should be understood before relying on its output.

1.  **Deterministic matching is not human judgment.** Rules can miss
    nuanced paraphrases or interpret ambiguous wording imperfectly.
2.  **A missing result is not proof of missing capability.** It means
    the submitted resume did not provide sufficient evidence under the
    current rules.
3.  **Resume quality affects results.** Poor formatting, unusual
    layouts, scanned documents or extraction errors can reduce the
    quality of downstream matching.
4.  **JD structure varies.** Although extraction supports multiple
    formats, unusual layouts and ambiguous sections may still need
    review.
5.  **Manual evidence is candidate-provided.** It should be
    distinguished from evidence present in the uploaded resume.
6.  **Alignment score is not a hiring probability.** It is an internal
    summary of requirement-level outcomes.
7.  **No external accuracy benchmark is claimed.** Precision, recall,
    F1, recruiter agreement and real-world hiring outcomes have not been
    established by the test suite.
8.  **Production deployment is pending.** The repository is published,
    but a live hosted production service has not yet been verified.

------------------------------------------------------------------------

## Roadmap

The following items are planned or potential next steps, not claims of
completed functionality.

### Product and analysis

-   Broaden evaluation against diverse job descriptions and industries.
-   Build a labeled evaluation dataset for measuring extraction and
    matching quality.
-   Measure precision, recall, F1 and false-positive/false-negative
    behavior.
-   Improve evidence explanations and traceability.
-   Improve handling of scanned PDFs and complex document layouts.
-   Continue validating role-agnostic behavior across job families.
-   Add transparent resume-improvement suggestions grounded in missing
    or partial evidence.

### Engineering

-   Deploy the FastAPI backend to Render.
-   Deploy the React frontend to Vercel.
-   Configure production CORS and frontend API URL.
-   Add deployment smoke tests and monitoring.
-   Review upload storage, retention and privacy controls.
-   Add CI automation for Python tests and frontend builds.
-   Review dependency security and update the Starlette test-client
    deprecation path.

### Evaluation discipline

Before publishing any future accuracy or impact claim, define: - The
test dataset and sample size. - The ground-truth labeling process. - The
evaluation split and methodology. - The metric definition. - The date
and software version used.

This will make future quantitative claims reproducible and meaningful.

------------------------------------------------------------------------

## Release and deployment status

### Published source release

-   **Repository:** <https://github.com/TejavarmaD/JD-Resume-Analyzer>
-   **Branch:** `main`
-   **Commit:** `05c3d3c`
-   **Commit message:** `Build role-agnostic JD resume analysis web app`
-   **Release commit contents:** 46 files changed, 12,671 insertions and
    45 deletions.
-   **Push status:** Successfully pushed to GitHub on 18 November 2026.

### Deployment status

The application has **not yet been deployed to a public production
environment**.

The planned deployment arrangement is:

  -----------------------------------------------------------------------
  Component               Planned platform        Configuration
  ----------------------- ----------------------- -----------------------
  FastAPI backend         Render                  Install Python
                                                  requirements; start
                                                  Uvicorn

  React frontend          Vercel                  Build with Vite;
                                                  publish `dist`

  Frontend-to-backend     Environment             Set `VITE_API_URL` to
  connection              configuration           the actual Render
                                                  backend base URL
  -----------------------------------------------------------------------

Suggested Render configuration:

-   Root directory: repository root.
-   Build command: `pip install -r requirements.txt`
-   Start command:
    `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
-   Environment variable: `CORS_ORIGINS` set to the deployed frontend
    origin.

Suggested Vercel configuration:

-   Root directory: `frontend`.
-   Framework: Vite.
-   Build command: `npm run build`.
-   Output directory: `dist`.
-   Environment variable: `VITE_API_URL` set to the deployed Render
    backend base URL, without `/api`.

These are deployment instructions, not evidence that either service is
already live. After deployment, verify the health endpoint, CORS, resume
upload, analysis response and frontend rendering.

------------------------------------------------------------------------

## Engineering principles

The project has been guided by the following principles:

-   **Role-agnostic by design:** the supplied JD should drive the
    analysis, not a hardcoded target title.
-   **Evidence before score:** requirement-level support should remain
    inspectable.
-   **Deterministic core:** the same inputs and code/configuration
    should produce reproducible rule-based results.
-   **Separation of concerns:** parsing, classification, matching,
    scoring, API orchestration and UI rendering are separate
    responsibilities.
-   **Regression-tested changes:** bug fixes should include tests that
    protect the corrected behavior.
-   **Honest measurement:** test counts, build outputs, analysis
    examples and future targets must be labeled accurately.
-   **Privacy-conscious repository:** personal resumes and generated
    candidate data should not be part of the public source commit.

------------------------------------------------------------------------

## Contributing and feedback

Suggestions, bug reports and improvements are welcome. Useful reports
should include: - The type of JD structure that failed (without sharing
confidential job or candidate data). - The expected requirement
extraction or evidence result. - The actual behavior. - A minimal
reproducible example with personal information removed. - The relevant
test or environment details.

Please do not publish personal resumes, contact details or other
sensitive candidate information in public issues.

------------------------------------------------------------------------

## Disclaimer

EvidenceFirst is an informational decision-support tool. It does not
make hiring decisions, guarantee interview selection, verify employment
history, or determine a candidate's actual ability. Its output depends
on the quality of the supplied JD, resume extraction and deterministic
evaluation rules. Users should review the underlying evidence and use
their own judgment.

------------------------------------------------------------------------

**Built as an evidence-first engineering project: extract the
requirement, locate the evidence, explain the gap, and make the result
inspectable.**
