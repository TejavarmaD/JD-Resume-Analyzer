from pathlib import Path
import sys
import json
import shutil
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import extract_documents
import jd_analyzer
import structured_resume_parser
import structured_entity_extractor
import skill_tag_extractor
import resume_evidence_matcher
import matching_score_engine
import experience_eligibility


def extract_candidate_resume(file_path: Path) -> dict:
    """Extract and structure an uploaded candidate's resume."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".docx":
        resume_text = extract_documents.extract_docx(file_path)
        page_count = None
        empty_pages = []

    elif suffix == ".pdf":
        resume_text, page_count, empty_pages = (
            extract_documents.extract_pdf(file_path)
        )

    else:
        raise ValueError("Only PDF and DOCX resumes are supported.")

    if not resume_text or not resume_text.strip():
        raise ValueError(
            "No readable text was extracted. "
            "The PDF may be scanned or image-based."
        )

    parsed_resume = structured_resume_parser.parse_resume(
        resume_text
    )

    resume_entities = (
        structured_entity_extractor.build_entity_output(
            parsed_resume
        )
    )

    resume_entities["source_file"] = file_path.name

    warnings = list(parsed_resume.get("review_warnings", []))

    if empty_pages:
        warnings.append(
            f"Some PDF pages contained no extractable text: {empty_pages}"
        )

    return {
        "extraction": {
            "file_name": file_path.name,
            "file_type": suffix.lstrip("."),
            "page_count": page_count,
            "empty_pages": empty_pages,
            "character_count": len(resume_text),
        },
        "parsed_resume": parsed_resume,
        "resume_entities": resume_entities,
        "review_warnings": warnings,
    }


def analyze_candidate_jd(jd_text: str) -> dict:
    """Analyze a supplied job description and generate skill tags."""

    if not isinstance(jd_text, str) or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    jd_data = jd_analyzer.analyze_jd(jd_text)

    requirements = jd_data.get("requirements", [])

    if not isinstance(requirements, list) or not requirements:
        raise ValueError(
            "No job requirements could be extracted. "
            "Add recognized section headings and bullet-point requirements "
            "to the job description."
        )

    compiled_dictionary = skill_tag_extractor.compile_dictionary()

    tagged_requirements = [
        skill_tag_extractor.build_requirement_output(
            requirement,
            compiled_dictionary,
        )
        for requirement in requirements
    ]

    tag_data = {
        "schema_version": "1.0",
        "tagging_method": "deterministic_dictionary_matching",
        "source": {
            "analysis_type": jd_data.get("analysis_type"),
        },
        "summary": skill_tag_extractor.build_summary(
            tagged_requirements
        ),
        "requirements": tagged_requirements,
    }

    return {
        "jd_analysis": jd_data,
        "skill_tags": tag_data,
    }


def match_candidate_evidence(
    jd_analysis: dict,
    skill_tags: dict,
    resume_entities: dict,
    resume_type: str,
) -> dict:
    """Match candidate resume evidence against JD requirements."""

    evidence_data = resume_evidence_matcher.build_output(
        skill_tags,
        resume_entities,
        resume_type,
        {},
    )

    return evidence_data


def score_candidate(
    jd_analysis: dict,
    skill_tags: dict,
    evidence_data: dict,
) -> dict:
    """Calculate a candidate's JD alignment score."""

    # Do not apply employer-specific experience policies
    # belonging to the original resume owner.
    eligibility_data = {
        "assessment": {
            "eligibility_status": "unverified",
            "reason": (
                "Experience eligibility requires candidate-specific "
                "verification. No employer-specific policies were applied."
            ),
        }
    }

    score_data = matching_score_engine.build_output(
        jd_analysis,
        skill_tags,
        evidence_data,
        eligibility_data,
    )

    return score_data


def analyze_candidate(resume_path: Path, jd_text: str) -> dict:
    """Run the complete candidate analysis pipeline in memory."""

    # 1. Extract and structure the uploaded resume.
    resume = extract_candidate_resume(resume_path)

    # 2. Analyze the job description and generate skill tags.
    jd = analyze_candidate_jd(jd_text)

    # 3. Match resume evidence against JD requirements.
    evidence = match_candidate_evidence(
        jd["jd_analysis"],
        jd["skill_tags"],
        resume["resume_entities"],
        resume["extraction"]["file_type"],
    )

    # 4. Calculate the candidate alignment score.
    score = score_candidate(
        jd["jd_analysis"],
        jd["skill_tags"],
        evidence,
    )

    return {
        "resume": {
            "extraction": resume["extraction"],
            "review_warnings": resume["review_warnings"],
        },
        "jd_analysis": jd["jd_analysis"],
        "skill_tags": jd["skill_tags"],
        "evidence": evidence,
        "score": score,
    }

def save_candidate_run(
    resume_path: Path,
    analysis_result: dict,
) -> dict:
    """Save one candidate's analysis in an isolated run directory."""

    resume_path = Path(resume_path)

    if not resume_path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {resume_path}"
        )

    runs_directory = PROJECT_ROOT / "candidate_runs"
    run_id = str(uuid.uuid4())
    run_directory = runs_directory / run_id

    run_directory.mkdir(parents=True, exist_ok=False)

    saved_resume = run_directory / f"resume{resume_path.suffix.lower()}"
    shutil.copy2(resume_path, saved_resume)

    analysis_file = run_directory / "analysis.json"

    with analysis_file.open("w", encoding="utf-8") as file:
        json.dump(
            analysis_result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return {
        "run_id": run_id,
        "run_directory": str(run_directory),
        "resume_file": str(saved_resume),
        "analysis_file": str(analysis_file),
    }
