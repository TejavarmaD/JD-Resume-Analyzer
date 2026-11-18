# EvidenceFirst — JD–Resume Analyzer

> **An evidence-driven, role-agnostic job description and resume analysis platform.**

EvidenceFirst is a full-stack application designed to evaluate how well a candidate's documented experience aligns with the requirements of a job description. Rather than relying exclusively on keyword overlap or producing an unexplained compatibility score, the platform extracts job requirements, structures resume information, identifies supporting evidence, evaluates requirement-level alignment, and presents traceable results.

The application combines a deterministic Python analysis engine with a React and TypeScript interface, supported by a FastAPI backend.

**Project status:** Functional local full-stack application; deployment preparation in progress.

---

## 1. Executive Overview

Recruitment and job-search workflows frequently involve comparing a candidate's resume with a job description. Traditional keyword-based approaches can produce misleading results:

- A resume may contain a keyword without demonstrating practical experience.
- A candidate may have relevant experience expressed using different terminology.
- A job description may describe responsibilities in paragraphs, bullets, or nested sections.
- A single overall compatibility score may conceal important qualification gaps.
- A missing keyword does not necessarily mean that the candidate lacks the underlying capability.

EvidenceFirst addresses these problems by treating the job description as a structured collection of requirements and the resume as a source of candidate evidence.

For every extracted requirement, the system attempts to determine whether the resume provides:

- **Matched evidence:** Relevant supporting evidence is identified.
- **Partial evidence:** Some relevant evidence exists, but it does not fully establish the requirement.
- **Missing evidence:** Sufficient supporting evidence has not been identified.

The application also identifies critical gaps, provides category-level alignment, and presents the evidence behind individual evaluations.

### Primary objective

Build a reliable, explainable and extensible JD–resume analysis platform that can evaluate different professional roles without requiring a separate matching engine for every job title.

The long-term objective is to help candidates understand:

1. Which job requirements their resumes demonstrably satisfy.
2. Which requirements have partial supporting evidence.
3. Which requirements are not demonstrated in the submitted resume.
4. Which important gaps deserve attention.
5. How their resume could communicate relevant experience more clearly.

**EvidenceFirst is an assessment and decision-support tool. It is not an automated hiring decision system.**

---

## 2. Product Philosophy: Evidence Before Scores

The central design principle is that a compatibility score should be supported by requirement-level evidence.

A keyword match alone is insufficient to establish professional competence.

For example, consider a job requirement:

> Develop and integrate REST APIs into production applications.

A resume mentioning REST APIs without describing any implementation or integration work should not automatically receive a full match.

The system therefore considers the relationship between:

- The extracted job requirement.
- Recognized skills and technical terms.
- Candidate resume evidence.
- The nature of the requirement.
- Whether the evidence demonstrates practical application.

This approach is intended to reduce superficial keyword matching and make the output more useful to candidates.

---

## 3. Development History: Resume Analyzer Plan 0–30

The following section consolidates the substantive engineering milestones across the Resume Analyzer development conversations, including architecture reviews, implementation iterations, regression investigations and product decisions.

It documents the evolution of the project rather than treating each conversation as an independent feature.

### Phase 1 — Establishing the deterministic foundation

**Initial development and baseline validation**

The project began with a Python-based JD–resume analysis pipeline.

The initial architecture included:

- Document text extraction.
- Structured resume parsing.
- Job description requirement extraction.
- Skill and technical-term identification.
- Resume evidence matching.
- Requirement-level scoring.
- Evidence interpretation.
- Experience eligibility assessment.

The first engineering priority was to establish a functioning deterministic baseline before introducing a web interface.

The existing Python engines were treated as the source of truth. The project deliberately avoided replacing working analysis logic simply to accommodate frontend development.

**Key engineering decisions**

- Preserve the original analysis pipeline.
- Separate document extraction from resume interpretation.
- Separate requirement extraction from evidence evaluation.
- Keep scoring independent from frontend presentation.
- Establish automated regression tests before substantial refactoring.

**Baseline:** 85 passing tests.

### Phase 2 — Full-stack application architecture

**Transition from a Python analysis workflow to a web application**

A React and TypeScript frontend was selected instead of Streamlit.

The backend was implemented using FastAPI, allowing the existing Python engines to be exposed through HTTP endpoints without duplicating their logic in JavaScript.

The resulting architecture became:

- React for the application interface.
- TypeScript for frontend type safety.
- Vite for frontend development and builds.
- FastAPI for HTTP request handling.
- Python modules for document processing and analysis.
- Existing deterministic engines for matching and scoring.

The application was organized around a candidate analysis workflow rather than a static dashboard.

**Product decisions**

- Use a single-candidate analysis workflow.
- Accept new resume and job description inputs.
- Keep the existing dashboard and legacy JSON-based workflow separate from fresh candidate analysis.
- Preserve analysis results when navigating between result tabs.
- Clear stale results when a new analysis begins.
- Avoid fabricated candidate data, batch rankings or mock matching results.

### Phase 3 — Dynamic candidate processing

**Removing dependence on a predefined candidate**

A critical architectural issue was the distinction between the original sample analysis and a genuinely reusable candidate analysis workflow.

The application needed to process the uploaded resume and supplied job description rather than rely on a predefined resume JSON or previously generated analysis.

The backend pipeline was developed to perform the following operations:

1. Extract text from the uploaded resume.
2. Parse the resume into structured information.
3. Extract candidate entities and supporting evidence.
4. Analyze the supplied job description.
5. Generate supplementary skill tags.
6. Match resume evidence against individual requirements.
7. Assess experience eligibility separately.
8. Calculate alignment scores.
9. Return a unified analysis result.

Candidate processing was isolated from the legacy dashboard workflow.

The existing scoring engine remained the source of truth.

### Phase 4 — Generic evidence evaluation

**Moving beyond role-specific manual matching**

The original matching logic contained specialized evaluation rules and manually maintained evidence relationships.

This created a scalability problem: requirements from different professional domains could require different hardcoded rules.

A generic requirement evaluator was introduced in `resume_evidence_matcher.py`.

Its supporting functions include:

- `normalize_requirement_term()`
- `extract_requirement_terms()`
- `split_requirement_clauses()`
- `find_clause_evidence()`
- `evidence_has_action()`
- `deduplicate_evidence()`
- `evaluate_generic_requirement()`

The main `evaluate_requirement()` function was integrated with the generic evaluator.

The implementation evaluates requirement clauses, searches for relevant evidence, and distinguishes practical evidence from weaker knowledge-only references.

It also preserves evidence source information and text offsets.

**Regression scenarios introduced**

- Product management roadmap and prioritization.
- Data analysis and report development.
- API integration versus general platform familiarity.
- Requirements without recognized skill tags.
- Knowledge-only evidence for practical requirements.
- Unrelated evidence.
- Evidence-source and offset preservation.

The initial generic evaluator test group contained seven tests.

**Important limitation:** This is deterministic lexical and rule-based evaluation, not a fully semantic understanding model. It can still miss paraphrases or misinterpret ambiguous terminology.

### Phase 5 — Generalizing job description extraction

**Removing the assumption that every requirement is a bullet point**

A significant extraction defect was identified: the original requirement extraction logic could skip standalone paragraphs because it expected list markers.

This was a major limitation because real job descriptions frequently contain:

- Complete sentences under unrecognized headings.
- Paragraph-style responsibilities.
- Numbered requirements.
- Bullet lists.
- Nested headings.
- Inline qualification statements.
- Multiple qualification sections.
- Technical stack summaries.

The extraction logic in `jd_analyzer.py` was refactored to handle these formats more generally.

Improvements included:

- Expanded section-heading recognition.
- Paragraph and bullet extraction.
- Numbered list recognition.
- Context-introduction filtering.
- Metadata filtering.
- Subsection-heading recognition.
- Independent source-section preservation.
- Qualification-section support.
- Priority detection for preferred and desirable requirements.

The implementation also added regression coverage for:

- Paragraphs under unrecognized headings.
- Job descriptions without conventional section headings.
- Mixed paragraph and bullet formats.
- Original source-section preservation.
- Metadata exclusion.
- Job-description header exclusion.
- Introductory outcome sentence exclusion.

**Extraction-format test group:** 7 passing tests.

### Phase 6 — Role-agnostic requirement classification

**Removing AI Engineer-specific assumptions**

The original classification logic contained a strong focus on AI engineering terminology.

This was incompatible with the intended product: a general-purpose JD–resume analyzer.

The classification function was generalized while retaining the existing five requirement-type labels:

- `qualification`
- `responsibility`
- `outcome`
- `soft_skill`
- `skill`

The revised logic recognizes general professional activities, qualifications, responsibilities, outcomes and interpersonal capabilities.

Examples include:

- Developing applications.
- Managing projects.
- Conducting analysis.
- Delivering reports.
- Leading teams.
- Collaborating with stakeholders.
- Managing product roadmaps.
- Demonstrating relevant professional experience.

A targeted responsibility-section exception was retained to preserve existing tests without classifying every sentence beginning with words such as "use" as a responsibility.

**Scoring design decision**

Professional domain was removed as a determinant of requirement importance.

Category weights were neutralized, while requirement priority remained meaningful.

This prevents a requirement from receiving greater importance merely because it belongs to an AI or software engineering category.

### Phase 7 — Role-agnostic category classification

The original category system was strongly oriented toward AI engineering.

It was expanded into a broader professional-domain taxonomy.

The current category dictionary includes:

- `software_engineering`
- `data_analytics`
- `data_engineering`
- `artificial_intelligence`
- `generative_ai_llm`
- `retrieval_information_systems`
- `agentic_systems`
- `cloud_devops`
- `evaluation_reliability`
- `security_responsible_practices`
- `product_management`
- `project_management`
- `business_operations`
- `design`
- `finance`
- `professional_skills`
- `qualifications_experience`

Unclassified or ambiguous requirements use:

- `general`

The classifier was improved to use normalized text and word-boundary matching rather than unrestricted substring matching.

Tie handling was also improved:

- Clearly stronger category evidence wins.
- Equally supported category classifications fall back to `general`.
- Requirements are not forced into a category merely to eliminate general classifications.

**Role-agnostic category test group:** 20 passing tests.

### Phase 8 — Scoring and evidence reliability

The scoring engine was reviewed separately from extraction and evidence interpretation.

The project retains the existing three evaluation statuses:

| Status | Score points |
|---|---:|
| Matched | 1.0 |
| Partial | 0.5 |
| Missing | 0.0 |

Requirement priority weights:

| Priority | Weight |
|---|---:|
| Must have | 1.0 |
| Good to have | 0.5 |
| Context | 0.0 |

The category/domain weighting was neutralized.

The scoring engine continues to validate the consistency of requirement IDs and requirement text across the analysis and matching inputs.

Critical gaps are identified when a must-have requirement is not fully matched.

Additional tests cover:

- All requirements matched.
- All requirements missing.
- Matching input consistency.
- Requirement-level score calculation.
- Critical-gap identification.

Evidence status and experience eligibility remain separate components rather than being merged into the overall scoring logic.

### Phase 9 — API reliability and input validation

The FastAPI backend was strengthened to handle invalid uploads and malformed inputs.

Implemented controls include:

- PDF and DOCX extension validation.
- PDF signature validation.
- DOCX ZIP-container validation.
- Verification of `word/document.xml`.
- Empty-file rejection.
- Empty job-description rejection.
- Maximum resume size of 10 MB.
- Maximum job-description length of 50,000 characters.
- Streaming upload-size validation.
- Safe error responses.
- Unexpected-exception logging.
- Upload resource cleanup.
- Unique UUID-based analysis identifiers.

The frontend also implements corresponding validation and request-handling safeguards.

These include:

- File extension checks.
- File-size checks.
- Basic file-signature checks.
- Job-description length validation.
- Response-shape validation.
- Request timeout handling.
- Duplicate-submission prevention.
- Request cancellation on component unmount.

The live analysis endpoint was changed to use stateless request processing and return a unique run identifier without persisting uploaded candidate documents on the server.

The separate local run-saving utility remains available for local development and testing.

### Phase 10 — Frontend integration and user experience

The frontend evolved into a React + TypeScript application.

Its main workflow is:

1. Upload a resume.
2. Provide a job description.
3. Submit the analysis.
4. Review the overall alignment.
5. Explore individual requirements.
6. Inspect critical gaps.
7. Review supporting evidence and limitations.

The results interface includes separate views for:

- Overview.
- Requirements.
- Critical Gaps.

The frontend consumes the actual FastAPI analysis response.

It does not independently calculate scores or invent matching results.

The interface uses a visual palette based on:

- Powder Blue: `#8DB9F0`
- Soft Lavender White: `#E9E8F8`
- Warm Sunset Peach: `#F5B69E`

### Phase 11 — Deployment preparation

The project is being prepared for publication through GitHub and deployment.

The current repository uses:

- Git branch: `main`
- GitHub remote: `JD-Resume-Analyzer`

The deployment architecture is being evaluated separately because the application processes uploaded documents and performs Python-based analysis.

The existing 10 MB resume-upload limit must be considered when choosing a hosting platform.

No production deployment should be considered complete until the frontend, backend, upload workflow, environment configuration and error handling have been verified in the deployed environment.

---

## 4. System Architecture

### Technology stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React 18 | User interface |
| Frontend language | TypeScript | Type-safe application logic |
| Build tooling | Vite 6 | Development and production builds |
| UI icons | Lucide React | Interface icons |
| Backend | FastAPI | HTTP API and validation |
| Backend language | Python | Analysis and processing |
| PDF extraction | pdfplumber | PDF text extraction |
| DOCX extraction | python-docx | Word document extraction |
| Data processing | Python standard libraries | Parsing, matching and transformations |
| Testing | pytest and unittest | Regression and integration validation |
| Version control | Git and GitHub | Source management |

### High-level architecture

```text
                    USER
                      |
                      v
          REACT + TYPESCRIPT FRONTEND
                      |
              Resume + Job Description
                      |
                      v
                 FASTAPI
                      |
             Input Validation Layer
                      |
                      v
             CANDIDATE PIPELINE
                      |
          +-----------+-----------+
          |                       |
          v                       v
    RESUME PROCESSING         JD PROCESSING
          |                       |
    Document Extraction      Requirement Extraction
          |                       |
    Resume Parsing           Requirement Classification
          |                       |
    Entity Extraction        Priority Detection
          |                       |
          v                       v
    RESUME EVIDENCE          SKILL TAG EXTRACTION
          |                       |
          +-----------+-----------+
                      |
                      v
              EVIDENCE MATCHING
                      |
                      v
           EXPERIENCE ELIGIBILITY
                      |
                      v
              SCORING ENGINE
                      |
                      v
             UNIFIED API RESPONSE
                      |
                      v
             REACT RESULTS VIEWS
```

### Repository structure

```text
JD_Resume Analyzer/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── candidate_pipeline.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── CandidateAnalyzer.tsx
│   │   ├── main.tsx
│   │   └── ...
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── extract_documents.py
├── structured_resume_parser.py
├── structured_entity_extractor.py
├── jd_analyzer.py
├── skill_tag_dictionary.py
├── skill_tag_extractor.py
├── resume_evidence_matcher.py
├── matching_score_engine.py
├── evidence_status_engine.py
├── experience_eligibility.py
│
├── test_candidate_api.py
├── test_candidate_pipeline.py
├── test_jd_extraction_formats.py
├── test_role_agnostic_extraction.py
├── test_role_agnostic_categories.py
├── test_generic_requirement_evaluator.py
├── test_matching_score_engine.py
├── test_resume_evidence_matcher.py
├── test_evidence_status_engine.py
├── test_resume_generalization.py
├── test_structured_entities.py
├── test_structured_parser.py
├── test_skill_tag_extractor.py
├── test_skill_tag_schema.py
├── test_compare_entity_outputs.py
├── test_jd_requirement_classification.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

Generated data, personal documents, local environments, backups and other development artifacts are intentionally excluded from the published source repository.

---

## 5. Core Processing Components

### 5.1 Document extraction — `extract_documents.py`

Responsible for extracting readable text from supported resume formats.

Supported formats:

- PDF
- DOCX

PDF processing uses `pdfplumber`.

DOCX processing uses `python-docx`.

The extraction layer is kept separate from resume interpretation so that document handling and candidate-data analysis can evolve independently.

### 5.2 Structured resume parsing — `structured_resume_parser.py`

Transforms extracted resume text into structured candidate information.

The parser identifies resume sections and organizes information for downstream processing.

### 5.3 Structured entity extraction — `structured_entity_extractor.py`

Extracts structured entities and evidence from the parsed resume.

The resulting information is used by the matching engine rather than relying solely on a flat collection of keywords.

### 5.4 Job description analysis — `jd_analyzer.py`

The JD analyzer extracts individual requirements and associated metadata.

Each requirement can contain:

- Requirement ID.
- Requirement text.
- Category.
- Priority.
- Requirement type.
- Category weight.
- Base weight.
- Original source section.
- Source evidence.

The extraction process attempts to preserve the relationship between the requirement and its original job-description context.

### 5.5 Skill tag extraction — `skill_tag_extractor.py`

Recognizes explicitly mentioned technical and professional terms using a versioned dictionary.

The current supplementary tag categories are:

- Concepts.
- Technologies.
- Platforms.
- Standards.

The dictionary uses explicit aliases, case-insensitive matching and phrase-boundary recognition.

Longer phrases receive precedence over shorter overlapping aliases.

The tag extractor is a supplementary recognition layer, not the sole source of requirement matching.

### 5.6 Evidence matching — `resume_evidence_matcher.py`

Evaluates whether the candidate's resume contains evidence relevant to a job requirement.

The generic evaluator considers requirement terms and clauses and attempts to identify supporting evidence.

The output preserves evidence details so that the result can be traced back to the source resume.

### 5.7 Evidence status — `evidence_status_engine.py`

Interprets evidence strength and classifies the resulting match status.

The status system maintains a consistent interface across the application:

- Matched.
- Partial.
- Missing.

### 5.8 Experience eligibility — `experience_eligibility.py`

Handles experience-related eligibility assessment separately from skill and responsibility matching.

An unverified eligibility result should not be interpreted as a confirmed rejection or an automatically established qualification.

### 5.9 Matching and scoring — `matching_score_engine.py`

Calculates the overall alignment and category-level results using the established requirement statuses and priority weights.

The scoring engine remains independent of the frontend and is the source of truth for the analysis score.

---

## 6. Role-Agnostic Design

Role independence is a central architectural requirement.

The system should not assume that every candidate is applying for an AI engineering position.

It should be capable of processing job descriptions for roles such as:

| Professional domain | Example requirements |
|---|---|
| Data Analyst | SQL, reporting, statistical analysis, visualization |
| Data Scientist | Machine learning, experimentation, predictive modelling |
| Data Engineer | ETL, data pipelines, warehouses, orchestration |
| Software Engineer | Programming, APIs, testing, application architecture |
| AI Engineer | LLMs, RAG, agent workflows, model evaluation |
| Product Manager | Product strategy, roadmaps, prioritization, user stories |
| Project Manager | Project delivery, scheduling, coordination, risk management |
| Business Analyst | Business requirements, process analysis, stakeholder communication |
| Finance Professional | Financial analysis, forecasting, budgeting, reporting |
| UX/UI Designer | User research, wireframes, usability and interaction design |

These examples demonstrate intended coverage, not a claim that every possible role has been independently benchmarked.

### How role independence is achieved

1. Requirements are extracted from the supplied job description.
2. Requirement types are determined using general classification rules.
3. Categories are assigned using a broader professional-domain taxonomy.
4. Supplementary skill tags are generated from the extracted text.
5. Evidence is evaluated against the requirement itself.
6. Scoring uses requirement priority rather than professional-domain importance.

The job title is therefore not intended to dictate a fixed list of expected skills.

A Product Manager job description should be evaluated against its actual product requirements, not against an AI Engineer skill dictionary.

---

## 7. Requirement Classification and Prioritization

The analyzer distinguishes between different kinds of job requirements.

| Requirement type | Purpose |
|---|---|
| Qualification | Education, certifications and professional experience |
| Responsibility | Work activities and responsibilities |
| Outcome | Expected deliverables or results |
| Soft skill | Collaboration, communication and interpersonal capabilities |
| Skill | Technical, functional or domain-specific capabilities |

Priority is assessed independently.

| Priority | Interpretation |
|---|---|
| Must have | Explicitly required or essential |
| Good to have | Preferred or desirable |
| Context | Contextual information, where applicable |

The system preserves requirement-level information so that the results can be examined independently of the overall score.

---

## 8. Evidence-First Matching Methodology

The matching process distinguishes between evidence of familiarity and evidence of practical implementation.

For example:

| Resume evidence | Requirement | Expected interpretation |
|---|---|---|
| "Familiar with Docker" | Deploy and maintain containerized applications | Potentially partial |
| "Built and deployed Dockerized services" | Deploy and maintain containerized applications | Stronger practical evidence |
| "Worked with APIs" | Design and integrate REST APIs | Requires further evidence |
| No relevant resume evidence | Develop production data pipelines | Missing |

These are illustrative examples. Actual classifications depend on the extracted requirement, candidate evidence and evaluator rules.

### Matching statuses

**Matched**

Relevant evidence supports the requirement sufficiently under the current evaluation rules.

**Partial**

Some relevant evidence is available, but the resume does not establish the complete requirement.

**Missing**

The evaluator has not identified sufficient supporting evidence.

A missing status means that the submitted resume does not demonstrate the requirement to the evaluator. It does not prove that the candidate lacks the capability.

### Explainability

The result structure retains requirement identifiers and evidence information so that individual evaluations can be reviewed.

This is important because a numerical score without supporting evidence is difficult to validate or improve.

---

## 9. Scoring Methodology

The scoring engine calculates a deterministic, weighted alignment score using the evidence status assigned to each extracted job requirement.

### Evidence status points

| Evidence status | Points |
|---|---:|
| Matched | 1.0 |
| Partial | 0.5 |
| Missing | 0.0 |

### Requirement weights

Each JD requirement receives a `base_weight` from the JD analysis output.

The JD analyzer's `base_weight` already incorporates category and priority weighting. The scoring engine uses this value directly and does not apply another priority multiplier.

If `base_weight` is absent, the scoring engine defaults to `1.0`. Negative weights are rejected.

### Alignment formula

For each requirement:

\[
E(r)=P(r)\times W(r)
\]

where:

- \(P(r)\) is the evidence-status point value.
- \(W(r)\) is the requirement's `base_weight`.

The overall alignment score is:

\[
\text{Alignment}=
\frac{\sum_{r\in R}E(r)}
{\sum_{r\in R}W(r)}
\times100
\]

The engine raises an error if the total requirement weight is zero.

### Critical gaps

A requirement is considered a critical gap when:

- Its priority is `must_have`.
- Its evidence status is not `matched`.

A partial match therefore remains a critical gap for a must-have requirement.

### Category scores and diagnostic tags

The engine also calculates category-level scores and evidence counts. Skill tags provide diagnostic information and do not independently add points to the overall alignment score.

### Scoring limitations

The score is a deterministic alignment indicator, not:

- A probability of receiving an interview.
- A prediction of hiring success.
- A measure of a candidate's complete professional capability.
- A benchmarked measure of model accuracy.

The score depends on JD extraction, requirement weights, resume extraction quality and evidence-matching decisions.

## 10. Quantitative Development and Validation

The following figures are taken from recorded project validation milestones.

### Automated test progression

| Development milestone | Passing tests |
|---|---:|
| Initial deterministic baseline | 85 |
| Generic evaluator and related integration milestone | 112 |
| Role-agnostic classification and weighting milestone | 131 |
| Role-agnostic category expansion milestone | 151 |

These are successive test-suite snapshots. They should not be added together as if they represent unique tests.

### Latest recorded validation

| Validation metric | Result |
|---|---:|
| Python tests passed | **151** |
| Subtests passed | **49** |
| Test failures | **0** |
| Warnings | 1 |
| Targeted candidate API and pipeline tests | 12 passed |
| Generic requirement evaluator tests | 7 passed |
| Role-agnostic category tests | 20 passed |
| JD extraction-format tests | 7 passed |
| Role-agnostic extraction tests | 5 passed |

The remaining warning is a Starlette deprecation warning concerning use of `httpx` with `starlette.testclient`. It did not cause a test failure.

### Historical analysis snapshot: AI Engineer job description

One recorded JD extraction produced:

**72 extracted requirements**

| Category | Requirements |
|---|---:|
| Generative AI / LLM | 15 |
| Agentic Systems | 10 |
| Retrieval / Information Systems | 9 |
| Evaluation / Reliability | 8 |
| Professional Skills | 6 |
| Software Engineering | 6 |
| Cloud / DevOps | 6 |
| General | 5 |
| Security / Responsible Practices | 3 |
| Qualifications / Experience | 2 |
| Data Analytics | 1 |
| Artificial Intelligence | 1 |
| **Total** | **72** |

Priority distribution:

- Must-have: 65
- Good-to-have: 7

The remaining general classifications are intentional where the category evidence is ambiguous or evenly supported.

### Earlier dashboard analysis snapshot

A separate historical analysis contained:

| Metric | Result |
|---|---:|
| Extracted requirements | 68 |
| Alignment score | 21.41% |
| Matched | 7 |
| Partial | 16 |
| Missing | 45 |
| Critical gaps | 54 |
| Experience eligibility | Unverified |

These figures describe one specific historical resume/JD comparison. They are not a universal product benchmark.

### Frontend validation

The React production build was successfully completed during local validation.

The Vite build transformed 1,578 modules in the recorded build.

The local frontend and FastAPI integration were also verified during development.

---

## 11. API Architecture

The FastAPI application is defined in:

`backend/app/main.py`

The candidate processing pipeline is defined in:

`backend/app/candidate_pipeline.py`

### Main endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/dashboard` | Legacy dashboard analysis |
| `GET /api/requirements` | Legacy requirement listing |
| `GET /api/requirements/{requirement_id}` | Legacy requirement detail |
| `POST /api/candidates/analyze` | Analyze an uploaded resume against a supplied JD |

The legacy dashboard endpoints are separate from the live candidate upload workflow. They read existing local analysis files and should not be confused with the dynamic candidate analysis endpoint.

### Upload validation

The live candidate endpoint currently enforces:

| Validation | Limit or rule |
|---|---|
| Resume formats | PDF and DOCX |
| Maximum resume size | 10 MB |
| Maximum JD length | 50,000 characters |
| Empty resume | Rejected |
| Empty JD | Rejected |
| Invalid PDF signature | Rejected |
| Invalid DOCX container | Rejected |
| Missing DOCX document XML | Rejected |

### Analysis identifiers and persistence

The live analysis endpoint generates a UUID for each analysis.

Uploaded files are processed through temporary storage, and the live endpoint does not persist candidate resumes or analysis runs to the local `candidate_runs` directory.

A separate run-saving function remains in the pipeline for local use and testing.

### API documentation

When the backend is running locally, interactive API documentation is available at:

`http://localhost:8000/docs`

---

## 12. Local Installation and Execution

### Prerequisites

Install:

- Python 3.12 or a compatible supported Python version.
- Node.js and npm.
- Git.

### Step 1 — Clone the repository

```powershell
git clone https://github.com/TejavarmaD/JD-Resume-Analyzer.git
cd JD-Resume-Analyzer
```

### Step 2 — Install Python dependencies

For development and testing, install:

```powershell
python -m pip install -r requirements-dev.txt
```

For runtime-only installation:

```powershell
python -m pip install -r requirements.txt
```

### Step 3 — Start the backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend:

`http://localhost:8000`

API documentation:

`http://localhost:8000/docs`

### Step 4 — Install frontend dependencies

Open another terminal:

```powershell
cd frontend
npm ci
```

### Step 5 — Start the frontend

```powershell
npm run dev
```

Frontend:

`http://localhost:5173`

### Step 6 — Run the Python tests

From the project root:

```powershell
python -m pytest -q
```

### Step 7 — Build the frontend

From the frontend directory:

```powershell
npm run build
```

---

## 13. Security, Privacy and Data Handling

Resume documents contain personal and professional information. The application therefore needs to handle candidate data carefully.

Current implementation safeguards include:

- File-type validation.
- File-signature validation.
- Upload-size limits.
- Job-description length limits.
- Temporary file processing.
- Cleanup of uploaded temporary files.
- No persistence through the live candidate-analysis endpoint.
- Exclusion of personal PDF and DOCX documents from Git.
- Exclusion of environment files and generated candidate data through `.gitignore`.

### Important deployment considerations

Before public deployment, additional checks are required for:

- Production HTTPS.
- Hosting-provider request-body limits.
- Serverless execution limits.
- Rate limiting and abuse prevention.
- Privacy disclosures and user consent.
- Logging policies.
- Production error handling.
- Data retention and storage configuration.
- Dependency security.

The current local safeguards should not be interpreted as a complete production security certification.

---

## 14. Known Limitations

EvidenceFirst is a developing deterministic analysis system.

Its current limitations include:

1. **Lexical matching limitations:** Different ways of expressing the same professional capability may not always be recognized.
2. **Ambiguous requirements:** A requirement containing several independent expectations may need more sophisticated decomposition.
3. **Category ambiguity:** Some mixed-domain requirements may appropriately fall under `general`.
4. **Dictionary coverage:** Skill tags depend on explicitly maintained aliases and terminology.
5. **Resume quality:** Poorly structured, scanned or image-based documents may not produce reliable text extraction.
6. **Evidence interpretation:** The deterministic evaluator cannot guarantee human-level contextual understanding.
7. **Eligibility verification:** Some experience or qualification requirements may remain unverified.
8. **Benchmarking:** No independently validated accuracy percentage or comprehensive labelled benchmark has been established.
9. **Production deployment:** Hosting and production integration are still being prepared.

The application should communicate uncertainty rather than present unsupported conclusions as facts.

---

## 15. Future Roadmap

The following are planned enhancements, not claims of completed functionality.

### Analysis quality

- Expand cross-role validation datasets.
- Improve requirement clause decomposition.
- Improve synonym and paraphrase recognition.
- Reduce false-positive and false-negative matches.
- Introduce more systematic evaluation metrics.
- Compare deterministic results against human-reviewed annotations.

### Explainability

- More detailed evidence-to-requirement traceability.
- Stronger explanations for partial matches.
- Clearer distinction between absent evidence and verified lack of capability.
- Improved requirement relationship and overlap analysis.

### Application functionality

- Resume improvement recommendations.
- Evidence-backed resume tailoring.
- Downloadable analysis reports.
- Analysis history, subject to an explicit privacy and retention design.
- Improved accessibility and responsive layouts.

### AI-assisted capabilities

An optional LLM-assisted layer may be explored in the future.

Any such addition should be evaluated against the deterministic baseline and must not silently replace the scoring source of truth.

Potential areas include:

- Semantic requirement interpretation.
- Paraphrase recognition.
- Evidence explanation.
- Resume improvement suggestions.

Any AI-assisted functionality should be tested for hallucinations, unsupported claims, reproducibility and evidence traceability.

### Deployment

- Finalize frontend and backend hosting.
- Configure production API routing.
- Validate uploaded-document processing in production.
- Verify production limits against the existing 10 MB upload requirement.
- Add deployment-specific monitoring and operational safeguards.

---

## 16. Engineering Principles

The project follows several core engineering principles:

**1. Evidence over keyword frequency**

A keyword appearing in a resume should not automatically establish practical experience.

**2. Role independence**

The analysis should be driven by the job description rather than assumptions about a specific job title.

**3. Separation of concerns**

Extraction, parsing, classification, evidence matching, scoring, API handling and presentation should remain independently testable.

**4. Deterministic scoring**

The scoring engine should produce reproducible results for the same validated inputs and rules.

**5. Explainability**

Requirement-level results should retain their supporting evidence and reasons.

**6. Regression protection**

Every significant change should be supported by targeted tests and a full regression run.

**7. Honest uncertainty**

The system should distinguish missing evidence, partial evidence and unverified information rather than inventing certainty.

---

## 17. Project Summary

EvidenceFirst has evolved from a deterministic Python-based resume analysis pipeline into a full-stack application with a React and TypeScript frontend and a FastAPI backend.

The major engineering focus has been on building a reusable analysis architecture that can:

- Process PDF and DOCX resumes.
- Extract requirements from varied job description formats.
- Classify requirements independently of a fixed job title.
- Recognize supplementary technical and professional terminology.
- Evaluate resume evidence at the requirement level.
- Distinguish matched, partial and missing evidence.
- Calculate weighted alignment and identify critical gaps.
- Expose the analysis through a validated API.
- Present results through an interactive web application.

**The defining principle of EvidenceFirst is simple: a resume should be evaluated against what a job actually requires, and every meaningful assessment should be supported by evidence from the resume.**

---

## 18. Project Status and Validation Record

| Area | Status |
|---|---|
| PDF/DOCX text extraction | Implemented |
| Structured resume parsing | Implemented |
| Structured entity extraction | Implemented |
| JD requirement extraction | Implemented |
| Role-agnostic requirement classification | Implemented |
| Role-agnostic category taxonomy | Implemented |
| Supplementary skill tagging | Implemented |
| Generic evidence evaluation | Implemented |
| Requirement-level scoring | Implemented |
| Evidence status interpretation | Implemented |
| Experience eligibility assessment | Implemented |
| FastAPI candidate analysis endpoint | Implemented |
| Upload validation | Implemented |
| React + TypeScript frontend | Implemented |
| Local full-stack workflow | Validated |
| Python regression suite | 151 passed; 49 subtests passed |
| Frontend production build | Previously validated |
| GitHub publication of current changes | Pending |
| Production hosting configuration | Pending |
| Production deployment verification | Pending |

**Documentation note:** Development milestones and quantitative figures reflect recorded project states. Test counts represent successive test-suite runs, while historical analysis figures refer to specific inputs and must not be interpreted as universal performance measurements.
