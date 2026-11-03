import json
import re
import sys
from pathlib import Path

from skill_tag_dictionary import SKILL_DICTIONARY, DICTIONARY_VERSION


BASE_DIR = Path(__file__).resolve().parent
JD_TAGS_FILE = BASE_DIR / "jd_results" / "ai_engineer_jd_skill_tags.json"

MANUAL_EVIDENCE_FILE = (BASE_DIR / "jd_results" / "manual_evidence.json")

RESUME_FILES = {
    "docx": BASE_DIR / "structured_results" / "Tejavarma Dommaraju_Resume_entities.json",
    "pdf": BASE_DIR / "structured_results" / "Tejavarma Dommaraju(Resume)_entities.json",
}

OUTPUT_DIR = BASE_DIR / "jd_results"


# ---------------------------------------------------------
# EVIDENCE RULES FOR REQUIREMENTS WITHOUT SKILL TAGS
# ---------------------------------------------------------

NON_TAG_EVIDENCE_RULES = {
    "REQ-010": {
        "method": "evaluation_evidence",
        "groups": [
            {
                "label": "AI or model evaluation",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "LLM evaluation",
                    "evaluate model responses",
                    "response relevance",
                    "factual accuracy",
                    "grounding",
                    "retrieval accuracy",
                ],
            },
            {
                "label": "evaluation against source evidence",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "retrieved source documents",
                    "source documents",
                    "grounded responses",
                    "source-based evaluation",
                ],
            },
        ],
    },
    "REQ-016": {
        "method": "workflow_design_evidence",
        "groups": [
            {
                "label": "deterministic workflow",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "deterministic workflow",
                    "rule-based workflow",
                    "rule-based processing",
                ],
            },
            {
                "label": "agent autonomy decision",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "autonomous agent",
                    "agent autonomy",
                    "human approval",
                    "human-in-the-loop",
                ],
            },
        ],
    },
    "REQ-030": {
        "method": "collaboration_evidence",
        "groups": [
            {
                "label": "engineering or product team collaboration",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK", "ACTIVITIES"],
                "phrases": [
                    "collaborated with engineering teams",
                    "collaborated with product teams",
                    "collaborate with engineering teams",
                    "collaborate with product teams",
                    "cross-functional engineering teams",
                    "cross-functional product teams",
                    "engineering and product teams",
                    "engineering, product, and design teams",
                ],
            },
        ],
        "partial_phrases": [
            "collaborate with stakeholders",
            "stakeholder collaboration",
            "collaborated with stakeholders",
            "worked with the team",
        ],
    },
    "REQ-031": {
        "method": "technical_communication_evidence",
        "groups": [
            {
                "label": "technical communication",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK", "ACTIVITIES"],
                "phrases": [
                    "technical documentation",
                    "technical discussions",
                    "knowledge transfer",
                    "KT sessions",
                    "documented technical",
                    "code reviews",
                    "presented technical",
                ],
            },
        ],
    },
    "REQ-050": {
        "method": "education_evidence",
        "groups": [
            {
                "label": "bachelor's degree",
                "sections": ["EDUCATION"],
                "phrases": [
                    "bachelor of technology",
                    "B.Tech",
                    "bachelor's degree",
                    "bachelor of science",
                    "bachelor of engineering",
                ],
            },
            {
                "label": "relevant discipline",
                "sections": ["EDUCATION"],
                "phrases": [
                    "computer science",
                    "information technology",
                    "artificial intelligence",
                    "data science",
                ],
            },
        ],
    },
    "REQ-058": {
        "method": "analytical_problem_solving_evidence",
        "groups": [
            {
                "label": "analysis or investigation",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "analyzing data",
                    "analyzed data",
                    "investigating data issues",
                    "investigated data",
                    "root cause analysis",
                    "statistical analysis",
                    "data reconciliation",
                ],
            },
        ],
    },
    "REQ-059": {
        "method": "business_problem_translation_evidence",
        "groups": [
            {
                "label": "business need",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "business requirements",
                    "business problems",
                    "business needs",
                ],
            },
            {
                "label": "solution tied to business need",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "translate business requirements",
                    "practical AI solutions",
                    "analytics solutions",
                    "solutions for business users",
                ],
            },
        ],
    },
    "REQ-060": {
        "method": "feature_ownership_evidence",
        "groups": [
            {
                "label": "development",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "developed",
                    "develop, test",
                    "built and",
                    "designed and implemented",
                ],
            },
            {
                "label": "testing",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "tested",
                    "test cases",
                    "unit testing",
                    "integration testing",
                ],
            },
            {
                "label": "deployment or delivery",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "deployed",
                    "deployment",
                    "delivered end-to-end",
                    "implemented and released",
                ],
            },
        ],
    },
    "REQ-061": {
        "method": "communication_collaboration_evidence",
        "groups": [
            {
                "label": "communication",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK", "ACTIVITIES"],
                "phrases": [
                    "communicate technical concepts",
                    "presentations",
                    "knowledge transfer",
                    "stakeholder communication",
                    "presented findings",
                ],
            },
            {
                "label": "collaboration",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK", "ACTIVITIES"],
                "phrases": [
                    "collaborate with stakeholders",
                    "cross-functional collaboration",
                    "stakeholder collaboration",
                    "collaborated with",
                ],
            },
        ],
    },
    "REQ-063": {
        "method": "learning_adaptability_evidence",
        "groups": [
            {
                "label": "active learning",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK", "ACTIVITIES"],
                "phrases": [
                    "independently learned",
                    "self-directed learning",
                    "upskilled",
                    "learning new technologies",
                    "researched and prototyped",
                    "adapted to",
                    "continuous learning",
                ],
            },
        ],
    },
    "REQ-066": {
        "method": "agentic_workflow_evidence",
        "groups": [
            {
                "label": "agent implementation",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "developed AI agents",
                    "develop, test, and deploy AI agents",
                    "implemented agentic workflows",
                    "built AI agents",
                ],
            },
            {
                "label": "tools or safeguards",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "tool integration",
                    "integrated external tools",
                    "human approval",
                    "safeguards",
                    "access controls",
                    "guardrails",
                ],
            },
        ],
    },
    "REQ-067": {
        "method": "evaluation_testing_evidence",
        "groups": [
            {
                "label": "AI testing",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "LLM testing",
                    "tested AI agents",
                    "test cases",
                    "automated tests",
                    "evaluation dataset",
                    "regression tests",
                ],
            },
            {
                "label": "repeatable evaluation",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "repeatable evaluation",
                    "evaluation framework",
                    "benchmark",
                    "measured response quality",
                    "tracked evaluation metrics",
                ],
            },
        ],
    },
    "REQ-068": {
        "method": "deployment_monitoring_evidence",
        "groups": [
            {
                "label": "application deployment",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "deployed applications",
                    "deployed AI agents",
                    "production deployment",
                    "deployed to production",
                ],
            },
            {
                "label": "application monitoring",
                "sections": ["WORK EXPERIENCE", "PROJECT WORK"],
                "phrases": [
                    "application monitoring",
                    "production monitoring",
                    "monitored application",
                    "logging and monitoring",
                    "tracked production performance",
                ],
            },
        ],
    },
}


# ---------------------------------------------------------
# SPECIAL REQUIREMENT RULES
# ---------------------------------------------------------

SPECIAL_REQUIREMENT_RULES = {
    "REQ-019": {
        "method": "python_code_quality_evidence",
        "phrases": [
            "modular code",
            "modular and reusable",
            "reusable code",
            "maintainable code",
            "software engineering best practices",
            "clean code",
        ],
    },
    "REQ-038": {
        "method": "working_llm_application_evidence",
        "phrases": [
            "built an LLM-powered application",
            "developed an LLM-powered application",
            "built a working LLM application",
            "developed a working LLM application",
            "LLM-based application",
            "LLM-powered application",
        ],
    },
    "REQ-047": {
        "method": "explicit_experience_duration",
        "patterns": [
            r"\b2\+?\s+years?\b",
            r"\bmore than 2 years\b",
            r"\bat least 2 years\b",
            r"\bthree years\b",
            r"\b3\+?\s+years?\b",
            r"\b4\+?\s+years?\b",
            r"\b5\+?\s+years?\b",
        ],
    },
    "REQ-064": {
        "method": "reliable_llm_feature_evidence",
        "phrases": [
            "reliable LLM application",
            "reliable LLM features",
            "improved LLM reliability",
            "LLM application reliability",
            "reliability testing",
            "validated LLM outputs",
            "validated model responses",
        ],
    },
}


# ---------------------------------------------------------
# REQUIREMENT-SPECIFIC TAG POLICIES
# ---------------------------------------------------------

REQUIREMENT_TAG_POLICIES = {
    "REQ-032": {
        "method": "python_proficiency_evidence",
        "tag": "python",
        "phrases": [
            "proficient in Python",
            "strong proficiency in Python",
            "high proficiency in Python",
        ],
        "allowed_sections": [
            "EXECUTIVE SUMMARY",
            "WORK EXPERIENCE",
            "PROJECT WORK",
            "SKILLS",
        ],
    },
        "REQ-002": {
        "method": "model_api_integration_evidence",
        "api_tag": "api",
        "platform_tags": [
            "openai",
            "azure_openai",
            "anthropic",
            "google_gemini",
        ],
        "allowed_sections": [
            "WORK EXPERIENCE",
            "PROJECT WORK",
        ],
    },
    "REQ-004": {
        "method": "implemented_llm_use_case_evidence",
        "use_case_tags": [
            "question_answering",
            "information_extraction",
            "content_generation",
        ],
        "allowed_sections": [
            "WORK EXPERIENCE",
            "PROJECT WORK",
        ],
    },
    "REQ-048": {
        "method": "working_llm_application_evidence",
        "tag": "llm",
        "allowed_sections": [
            "WORK EXPERIENCE",
            "PROJECT WORK",
        ],
    },
}


# ---------------------------------------------------------
# ALIAS COMPILATION
# ---------------------------------------------------------

def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def compile_aliases():
    """Build exact, case-insensitive patterns from the skill dictionary."""
    aliases = {}

    for tag, details in SKILL_DICTIONARY.items():
        values = set(details.get("aliases", []))
        values.add(details["display_name"])
        values.add(tag.replace("_", " "))

        patterns = []

        for alias in values:
            alias = alias.strip()

            if alias:
                patterns.append(
                    (
                        alias,
                        re.compile(
                            r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                            re.IGNORECASE,
                        ),
                    )
                )

        patterns.sort(key=lambda item: len(item[0]), reverse=True)
        aliases[tag] = patterns

    return aliases


ALIASES = compile_aliases()


# ---------------------------------------------------------
# RESUME SEGMENT EXTRACTION
# ---------------------------------------------------------

def add_segment(segments, section, record, field, text):
    """Add one source-backed text segment."""
    if not isinstance(text, str) or not text.strip():
        return

    segments.append({
        "section": section,
        "record": record,
        "field": field,
        "text": text.strip(),
    })


def build_resume_segments(resume):
    """Collect evidence from structured resume fields."""
    segments = []

    summary = resume.get("source_section_text", {}).get("EXECUTIVE SUMMARY")

    add_segment(
        segments,
        "EXECUTIVE SUMMARY",
        None,
        "source_section_text",
        summary,
    )

    for index, record in enumerate(
        resume.get("work_experience", {}).get("records", []),
        start=1,
    ):
        employer = record.get("employer", f"Work record {index}")

        for item_index, value in enumerate(
            record.get("responsibilities", []),
            start=1,
        ):
            add_segment(
                segments,
                "WORK EXPERIENCE",
                employer,
                f"responsibilities[{item_index}]",
                value,
            )

    for index, record in enumerate(
        resume.get("projects", {}).get("records", []),
        start=1,
    ):
        project_name = record.get("name", f"Project {index}")

        for item_index, value in enumerate(
            record.get("evidence", []),
            start=1,
        ):
            add_segment(
                segments,
                "PROJECT WORK",
                project_name,
                f"evidence[{item_index}]",
                value,
            )

    for index, record in enumerate(
        resume.get("skills", {}).get("records", []),
        start=1,
    ):
        category = record.get("category", f"Skill category {index}")

        for item_index, value in enumerate(
            record.get("items", []),
            start=1,
        ):
            add_segment(
                segments,
                "SKILLS",
                category,
                f"items[{item_index}]",
                value,
            )

    for index, record in enumerate(
        resume.get("education", {}).get("records", []),
        start=1,
    ):
        add_segment(
            segments,
            "EDUCATION",
            f"Education record {index}",
            "text",
            record.get("text"),
        )

    certification_data = resume.get("certifications_and_activities", {})

    for index, record in enumerate(
        certification_data.get("certifications", []),
        start=1,
    ):
        add_segment(
            segments,
            "CERTIFICATIONS",
            f"Certification {index}",
            "name",
            record.get("name"),
        )

    for index, record in enumerate(
        certification_data.get("activities", []),
        start=1,
    ):
        add_segment(
            segments,
            "ACTIVITIES",
            f"Activity {index}",
            "text",
            record.get("text"),
        )

    return segments


# ---------------------------------------------------------
# SENTENCE-LEVEL EVIDENCE
# ---------------------------------------------------------

def split_sentences(text):
    """Split evidence into sentence-like units."""
    parts = re.split(r"(?<=[.!?])\s+|[\r\n]+", text)

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


ACTION_PATTERN = re.compile(
    r"\b(?:built|build|developed|develop|implemented|integrated|"
    r"created|designed|deployed|tested|maintained|automated|"
    r"prototyped|configured|engineered|wrote|written)\b",
    re.IGNORECASE,
)

BUILD_ACTION_PATTERN = re.compile(
    r"\b(?:built|build|developed|develop|created|designed|engineered)\b",
    re.IGNORECASE,
)

INTEGRATION_ACTION_PATTERN = re.compile(
    r"\b(?:integrated|integrate|incorporated|incorporate)\b",
    re.IGNORECASE,
)

IMPLEMENTATION_SECTIONS = {
    "WORK EXPERIENCE",
    "PROJECT WORK",
}

KNOWLEDGE_SECTIONS = {
    "EXECUTIVE SUMMARY",
    "SKILLS",
    "CERTIFICATIONS",
    "EDUCATION",
    "ACTIVITIES",
}


def find_tag_evidence(tag, segments):
    """Find explicit dictionary aliases in resume evidence."""
    results = []

    for segment in segments:
        text = segment["text"]
        occupied_spans = []

        for alias, pattern in ALIASES.get(tag, []):
            for match in pattern.finditer(text):
                span = match.span()

                if any(
                    span[0] < existing[1] and span[1] > existing[0]
                    for existing in occupied_spans
                ):
                    continue

                occupied_spans.append(span)

                results.append({
                    "matched_text": match.group(0),
                    "dictionary_alias": alias,
                    "section": segment["section"],
                    "record": segment["record"],
                    "field": segment["field"],
                    "source_text": text,
                    "evidence": {
                        "start": match.start(),
                        "end": match.end(),
                    },
                })

    return results


def find_phrase_evidence(phrases, segments, allowed_sections=None):
    """Find literal evidence phrases in permitted resume sections."""
    results = []

    for segment in segments:
        if (
            allowed_sections
            and segment["section"] not in allowed_sections
        ):
            continue

        for phrase in phrases:
            pattern = re.compile(
                r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
                re.IGNORECASE,
            )

            for match in pattern.finditer(segment["text"]):
                results.append({
                    "matched_text": match.group(0),
                    "matched_rule_phrase": phrase,
                    "section": segment["section"],
                    "record": segment["record"],
                    "field": segment["field"],
                    "source_text": segment["text"],
                    "evidence": {
                        "start": match.start(),
                        "end": match.end(),
                    },
                })

    return results


def find_same_sentence_action(evidence):
    """Return evidence where a tag and an action verb share a sentence."""
    implementation = []

    for item in evidence:
        if item["section"] not in IMPLEMENTATION_SECTIONS:
            continue

        text = item.get("source_text", "")
        start = item["evidence"]["start"]
        end = item["evidence"]["end"]

        for sentence in split_sentences(text):
            sentence_start = text.find(sentence)

            if sentence_start < 0:
                continue

            sentence_end = sentence_start + len(sentence)

            if start < sentence_start or end > sentence_end:
                continue

            if ACTION_PATTERN.search(sentence):
                implementation.append({
                    **item,
                    "implementation_sentence": sentence,
                })

            break

    return implementation


def classify_tag_evidence(evidence):
    """Separate implementation evidence from knowledge-only mentions."""
    implementation = find_same_sentence_action(evidence)

    implementation_keys = {
        (
            item["section"],
            item["record"],
            item["field"],
            item["evidence"]["start"],
            item["evidence"]["end"],
        )
        for item in implementation
    }

    knowledge = [
        item
        for item in evidence
        if item["section"] in KNOWLEDGE_SECTIONS
        or (
            item["section"] in IMPLEMENTATION_SECTIONS
            and (
                item["section"],
                item["record"],
                item["field"],
                item["evidence"]["start"],
                item["evidence"]["end"],
            ) not in implementation_keys
        )
    ]

    return {
        "implementation": implementation,
        "knowledge": knowledge,
    }


# ---------------------------------------------------------
# REQUIREMENT TAGS AND ALTERNATIVES
# ---------------------------------------------------------

def get_requirement_tags(requirement):
    """Collect unique canonical tags from all four categories."""
    tags = []
    skill_tags = requirement.get("skill_tags", {})

    for category in (
        "concepts",
        "technologies",
        "platforms",
        "standards",
    ):
        for item in skill_tags.get(category, []):
            tag = item.get("tag")

            if tag and tag not in tags:
                tags.append(tag)

    return tags


# ---------------------------------------------------------
# SPECIAL REQUIREMENT EVALUATION
# ---------------------------------------------------------

def evaluate_special_requirement(requirement, segments):
    """Apply strict special rules for selected requirements."""
    requirement_id = requirement.get("requirement_id")
    rule = SPECIAL_REQUIREMENT_RULES.get(requirement_id)

    if not rule:
        return None

    if "phrases" in rule:
        evidence = find_phrase_evidence(
            rule["phrases"],
            segments,
            IMPLEMENTATION_SECTIONS,
        )

        evidence = [
            item
            for item in evidence
            if find_same_sentence_action([item])
        ]

    else:
        evidence = []

        patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in rule.get("patterns", [])
        ]

        for segment in segments:
            if segment["section"] not in IMPLEMENTATION_SECTIONS:
                continue

            for pattern in patterns:
                for match in pattern.finditer(segment["text"]):
                    evidence.append({
                        "matched_text": match.group(0),
                        "matched_rule_phrase": match.group(0),
                        "section": segment["section"],
                        "record": segment["record"],
                        "field": segment["field"],
                        "source_text": segment["text"],
                        "evidence": {
                            "start": match.start(),
                            "end": match.end(),
                        },
                    })

    if evidence:
        status = "matched"
        strength = "implementation"
        reason = (
            "Specific requirement evidence was found in "
            "work or project experience."
        )
    else:
        status = "missing"
        strength = "none"
        reason = (
            "The resume does not explicitly establish "
            "this specific requirement."
        )

    return {
        "status": status,
        "status_reason": reason,
        "evidence_strength": strength,
        "evaluation_method": rule["method"],
        "evidence": evidence,
    }


# ---------------------------------------------------------
# REQUIREMENT-SPECIFIC TAG POLICIES
# ---------------------------------------------------------

def filter_requirement_evidence(evidence, allowed_sections):
    """Keep only evidence from sections relevant to the requirement."""
    return [
        item
        for item in evidence
        if item.get("section") in allowed_sections
    ]



def evaluate_llm_application_policy(policy, segments):
    """
    Require LLM evidence, a build/development action, and an integration
    action in the same sentence.
    """
    matched_evidence = []
    partial_evidence = []

    for segment in segments:
        if segment["section"] not in policy["allowed_sections"]:
            continue

        text = segment["text"]

        llm_evidence = find_tag_evidence(
            policy["tag"],
            [segment],
        )

        for sentence in split_sentences(text):
            sentence_start = text.find(sentence)

            if sentence_start < 0:
                continue

            sentence_end = sentence_start + len(sentence)

            sentence_llm = [
                item
                for item in llm_evidence
                if (
                    item["evidence"]["start"] >= sentence_start
                    and item["evidence"]["end"] <= sentence_end
                )
            ]

            if not sentence_llm:
                continue

            has_build_action = bool(
                BUILD_ACTION_PATTERN.search(sentence)
            )

            has_integration_action = bool(
                INTEGRATION_ACTION_PATTERN.search(sentence)
            )

            sentence_evidence = [
                {
                    "tag": policy["tag"],
                    **item,
                }
                for item in sentence_llm
            ]

            if has_build_action and has_integration_action:
                matched_evidence.extend(sentence_evidence)

                matched_evidence.append({
                    "section": segment["section"],
                    "record": segment["record"],
                    "field": segment["field"],
                    "source_text": text,
                    "implementation_sentence": sentence,
                    "evidence_type": "build_and_integration_actions",
                })
            else:
                partial_evidence.extend(sentence_evidence)

    if matched_evidence:
        return {
            "status": "matched",
            "status_reason": (
                "LLM evidence and both building/developing and "
                "integration actions were found in the same sentence."
            ),
            "evidence_strength": "implementation",
            "evaluation_method": policy["method"],
            "evidence": matched_evidence,
        }

    if partial_evidence:
        return {
            "status": "partial",
            "status_reason": (
                "LLM implementation evidence exists, but the same "
                "sentence does not establish both building/developing "
                "and integration activities."
            ),
            "evidence_strength": "incomplete_implementation",
            "evaluation_method": policy["method"],
            "evidence": partial_evidence,
        }

    return {
        "status": "missing",
        "status_reason": (
            "No LLM application evidence was found in work "
            "or project experience."
        ),
        "evidence_strength": "none",
        "evaluation_method": policy["method"],
        "evidence": [],
    }

def evaluate_model_api_integration_policy(policy, segments):
    """
    Require API, model-platform and integration evidence in the
    same sentence and the same work/project segment.
    """
    matched_evidence = []
    partial_evidence = []

    for segment in segments:
        if segment["section"] not in policy["allowed_sections"]:
            continue

        text = segment["text"]

        api_evidence = find_tag_evidence(
            policy["api_tag"],
            [segment],
        )

        platform_evidence = {
            tag: find_tag_evidence(tag, [segment])
            for tag in policy["platform_tags"]
        }

        for sentence in split_sentences(text):
            sentence_start = text.find(sentence)

            if sentence_start < 0:
                continue

            sentence_end = sentence_start + len(sentence)

            def in_sentence(items):
                return [
                    item
                    for item in items
                    if sentence_start <= item["evidence"]["start"]
                    and item["evidence"]["end"] <= sentence_end
                ]

            api_matches = in_sentence(api_evidence)

            platform_matches = [
                {
                    "tag": tag,
                    **item,
                }
                for tag, items in platform_evidence.items()
                for item in in_sentence(items)
            ]

            if not api_matches and not platform_matches:
                continue

            sentence_evidence = [
                {
                    "tag": policy["api_tag"],
                    **item,
                }
                for item in api_matches
            ] + platform_matches

            if (
                api_matches
                and platform_matches
                and INTEGRATION_ACTION_PATTERN.search(sentence)
            ):
                matched_evidence.extend(sentence_evidence)
                matched_evidence.append({
                    "section": segment["section"],
                    "record": segment["record"],
                    "field": segment["field"],
                    "source_text": text,
                    "implementation_sentence": sentence,
                    "evidence_type": "api_model_integration",
                })
            else:
                partial_evidence.extend(sentence_evidence)

    if matched_evidence:
        return {
            "status": "matched",
            "status_reason": (
                "API, model-platform and integration-action evidence "
                "were found together in the same work or project sentence."
            ),
            "evidence_strength": "implementation",
            "evaluation_method": policy["method"],
            "evidence": matched_evidence,
        }

    if partial_evidence:
        return {
            "status": "partial",
            "status_reason": (
                "API or model-platform evidence exists in work or "
                "project experience, but complete integration evidence "
                "is not established."
            ),
            "evidence_strength": "incomplete_implementation",
            "evaluation_method": policy["method"],
            "evidence": partial_evidence,
        }

    return {
        "status": "missing",
        "status_reason": (
            "No qualifying API and model-platform integration evidence "
            "was found in work or project experience. Certification "
            "mentions are not accepted as integration evidence."
        ),
        "evidence_strength": "none",
        "evaluation_method": policy["method"],
        "evidence": [],
    }


def evaluate_llm_use_case_policy(policy, segments):
    """Match when at least one listed use case is implemented."""
    implementation_evidence = []
    knowledge_evidence = []

    for tag in policy["use_case_tags"]:
        evidence = find_tag_evidence(tag, segments)

        evidence = filter_requirement_evidence(
            evidence,
            policy["allowed_sections"],
        )

        classified = classify_tag_evidence(evidence)

        implementation_evidence.extend(
            {"tag": tag, **item}
            for item in classified["implementation"]
        )

        knowledge_evidence.extend(
            {"tag": tag, **item}
            for item in classified["knowledge"]
        )

    if implementation_evidence:
        return {
            "status": "matched",
            "status_reason": (
                "At least one listed use case has explicit "
                "implementation evidence in work or project experience."
            ),
            "evidence_strength": "implementation",
            "evaluation_method": policy["method"],
            "evidence": implementation_evidence,
        }

    if knowledge_evidence:
        return {
            "status": "partial",
            "status_reason": (
                "A listed use case is mentioned, but implementation "
                "evidence was not established."
            ),
            "evidence_strength": "knowledge_only",
            "evaluation_method": policy["method"],
            "evidence": knowledge_evidence,
        }

    return {
        "status": "missing",
        "status_reason": (
            "No listed use case was found in the resume."
        ),
        "evidence_strength": "none",
        "evaluation_method": policy["method"],
        "evidence": [],
    }

def evaluate_requirement_tag_policy(requirement, segments):
    """Apply requirement-specific evidence rules."""
    requirement_id = requirement.get("requirement_id")
    policy = REQUIREMENT_TAG_POLICIES.get(requirement_id)

    if not policy:
        return None

    if requirement_id == "REQ-002":
        return evaluate_model_api_integration_policy(
            policy,
            segments,
        )

    if requirement_id == "REQ-004":
        return evaluate_llm_use_case_policy(
            policy,
            segments,
        )

    if requirement_id == "REQ-032":
        evidence = find_phrase_evidence(
            policy["phrases"],
            segments,
            policy["allowed_sections"],
        )

        if evidence:
            return {
                "status": "matched",
                "status_reason": (
                    "Explicit Python proficiency wording was found "
                    "in the resume."
                ),
                "evidence_strength": "documented_proficiency",
                "evaluation_method": policy["method"],
                "evidence": evidence,
            }

        python_evidence = find_tag_evidence(
            policy["tag"],
            segments,
        )

        python_evidence = filter_requirement_evidence(
            python_evidence,
            policy["allowed_sections"],
        )

        return {
            "status": "partial" if python_evidence else "missing",
            "status_reason": (
                "Python is mentioned, but explicit proficiency "
                "is not established."
                if python_evidence
                else "No Python evidence was found."
            ),
            "evidence_strength": (
                "knowledge_only" if python_evidence else "none"
            ),
            "evaluation_method": policy["method"],
            "evidence": python_evidence,
        }

    if requirement_id == "REQ-048":
        return evaluate_llm_application_policy(
            policy,
            segments,
        )

    return None


# ---------------------------------------------------------
# TAG-BASED REQUIREMENT EVALUATION
# ---------------------------------------------------------

IMPLEMENTATION_REQUIRED_PATTERN = re.compile(
    r"\b(?:build|built|develop|developed|implement|implemented|"
    r"integrate|integrated|deploy|deployed|maintain|maintained|"
    r"hands-on|experience|practical|working application|pipeline)\b",
    re.IGNORECASE,
)


def evaluate_tag_requirement(requirement, segments):
    """Evaluate tag evidence without treating knowledge as implementation."""
    tags = get_requirement_tags(requirement)

    evidence_by_tag = {
        tag: find_tag_evidence(tag, segments)
        for tag in tags
    }

    alternative_groups = requirement.get("alternatives", [])

    alternative_tag_set = {
        tag
        for group in alternative_groups
        for tag in group.get("tags", [])
    }

    required_tags = [
        tag
        for tag in tags
        if tag not in alternative_tag_set
    ]

    all_evidence = [
        {"tag": tag, **item}
        for tag in tags
        for item in evidence_by_tag[tag]
    ]

    classified_by_tag = {
        tag: classify_tag_evidence(evidence_by_tag[tag])
        for tag in tags
    }

    implementation_tags = {
        tag
        for tag, result in classified_by_tag.items()
        if result["implementation"]
    }

    knowledge_tags = {
        tag
        for tag, result in classified_by_tag.items()
        if result["knowledge"]
    }

    requirement_text = requirement.get("requirement_text", "")

    implementation_expected = bool(
        IMPLEMENTATION_REQUIRED_PATTERN.search(requirement_text)
    )

    alternative_results = []

    for group in alternative_groups:
        options = group.get("tags", [])
        supported = []

        for tag in options:
            evidence_strength = classified_by_tag.get(
                tag,
                {"implementation": [], "knowledge": []},
            )

            if implementation_expected:
                if evidence_strength["implementation"]:
                    supported.append(tag)
            elif (
                evidence_strength["implementation"]
                or evidence_strength["knowledge"]
            ):
                supported.append(tag)

        alternative_results.append({
            "group_id": group.get("group_id"),
            "operator": "OR",
            "options": options,
            "supported_options": supported,
            "satisfied": bool(supported),
            "source_text": group.get("source_text"),
        })

    required_supported = all(
        tag in implementation_tags
        if implementation_expected
        else tag in implementation_tags or tag in knowledge_tags
        for tag in required_tags
    )

    alternatives_supported = all(
        group["satisfied"]
        for group in alternative_results
    )

    if required_supported and alternatives_supported:
        status = "matched"
        reason = (
            "All required tags have evidence at the strength "
            "required by the wording."
        )
        strength_label = (
            "implementation"
            if implementation_expected
            else "knowledge_or_implementation"
        )

    elif implementation_tags or knowledge_tags:
        status = "partial"
        reason = (
            "Some relevant tags are present, but the required "
            "implementation evidence or full tag coverage is incomplete."
        )
        strength_label = "mixed_or_knowledge_only"

    else:
        status = "missing"
        reason = (
            "No relevant resume evidence was found for "
            "the extracted tags."
        )
        strength_label = "none"

    matched_tags = sorted(implementation_tags | knowledge_tags)

    missing_tags = [
        tag
        for tag in tags
        if tag not in matched_tags
    ]

    return {
        "status": status,
        "status_reason": reason,
        "evidence_strength": strength_label,
        "evaluation_method": "tag_matching_with_sentence_level_evidence",
        "tag_coverage": {
            "total_tags": len(tags),
            "matched_tag_count": len(matched_tags),
            "missing_tag_count": len(missing_tags),
            "matched_tags": matched_tags,
            "missing_tags": missing_tags,
            "implementation_tags": sorted(implementation_tags),
            "knowledge_only_tags": sorted(
                knowledge_tags - implementation_tags
            ),
        },
        "alternative_groups": alternative_results,
        "evidence": all_evidence,
    }


# ---------------------------------------------------------
# NON-TAG REQUIREMENT EVALUATION
# ---------------------------------------------------------


def evaluate_non_tag_requirement(requirement, segments):
    """Evaluate requirements and preserve group-level evidence status."""
    rule = NON_TAG_EVIDENCE_RULES.get(
        requirement.get("requirement_id")
    )

    if not rule:
        return {
            "status": "missing",
            "status_reason": (
                "No configured evidence rule exists "
                "for this requirement."
            ),
            "evidence_strength": "none",
            "evaluation_method": "not_evaluable",
            "evidence_groups": [],
            "evidence": [],
        }

    group_results = []
    all_evidence = []

    permitted_sections = {
        section
        for group in rule["groups"]
        for section in group.get("sections", [])
    }

    partial_evidence = find_phrase_evidence(
        rule.get("partial_phrases", []),
        segments,
        permitted_sections,
    )

    for group in rule["groups"]:
        evidence = find_phrase_evidence(
            group["phrases"],
            segments,
            group.get("sections"),
        )

        group_status = "matched" if evidence else "missing"

        group_results.append({
            "label": group["label"],
            "status": group_status,
            "satisfied": group_status == "matched",
            "evidence_count": len(evidence),
            "evidence": evidence,
            "manual_evidence": [],
            "manual_evidence_count": 0,
        })

        all_evidence.extend(evidence)

    satisfied_count = sum(
        group["status"] == "matched"
        for group in group_results
    )

    total_groups = len(group_results)

    if satisfied_count == total_groups:
        status = "matched"
        reason = (
            "All configured evidence groups have explicit "
            "phrase-level support."
        )
        strength_label = (
            "implementation"
            if all(
                item["section"] in IMPLEMENTATION_SECTIONS
                for item in all_evidence
            )
            else "documented_qualification_or_knowledge"
        )

    elif satisfied_count:
        status = "partial"
        reason = (
            "Some configured evidence groups are supported; "
            "others are absent."
        )
        strength_label = "partial"

    elif partial_evidence:
        status = "partial"
        reason = (
            "Related evidence exists, but it does not explicitly "
            "establish the specific requirement."
        )
        strength_label = "partial"
        all_evidence.extend(partial_evidence)

    else:
        status = "missing"
        reason = (
            "The required evidence phrases were not found "
            "in permitted sections."
        )
        strength_label = "none"

    return {
        "status": status,
        "status_reason": reason,
        "evidence_strength": strength_label,
        "evaluation_method": rule["method"],
        "evidence_groups": group_results,
        "evidence": all_evidence,
    }


# ---------------------------------------------------------
# MAIN REQUIREMENT ROUTER
# ---------------------------------------------------------



def evaluate_requirement(requirement, segments):
    """Route each requirement to its strictest applicable evaluator."""
    requirement_id = requirement.get("requirement_id")

    policy_evaluation = evaluate_requirement_tag_policy(
        requirement,
        segments,
    )

    if policy_evaluation is not None:
        evaluation = policy_evaluation

    else:
        special_evaluation = evaluate_special_requirement(
            requirement,
            segments,
        )

        if special_evaluation is not None:
            evaluation = special_evaluation

        elif requirement_id in NON_TAG_EVIDENCE_RULES:
            evaluation = evaluate_non_tag_requirement(
                requirement,
                segments,
            )

        else:
            tags = get_requirement_tags(requirement)

            if tags:
                evaluation = evaluate_tag_requirement(
                    requirement,
                    segments,
                )
            else:
                evaluation = evaluate_non_tag_requirement(
                    requirement,
                    segments,
                )

    return {
        "requirement_id": requirement_id,
        "requirement_text": requirement.get("requirement_text"),
        **evaluation,
        "unmatched_jd_terms_for_review": requirement.get(
            "unmatched_terms",
            [],
        ),
    }


# ---------------------------------------------------------
# USER-CONFIRMED EVIDENCE
# ---------------------------------------------------------

def load_manual_evidence():
    """Load separately maintained user-confirmed evidence."""
    if not MANUAL_EVIDENCE_FILE.is_file():
        return {}

    data = load_json(MANUAL_EVIDENCE_FILE)

    if not isinstance(data, dict):
        raise ValueError("Manual evidence root must be an object.")

    return data.get("requirements", {})



def apply_manual_evidence(evaluation, requirement_id, manual_data):
    """
    Combine user-confirmed evidence with resume evaluation.
    Keep manual evidence separate from resume quotations.
    Support evidence-group-level manual confirmations.
    """
    manual_record = manual_data.get(requirement_id)

    if not manual_record:
        evaluation["resume_status"] = evaluation["status"]
        evaluation["manual_status"] = None
        evaluation["manual_evidence"] = []
        evaluation["manual_confirmation"] = None
        return evaluation

    manual_status = manual_record.get("status")

    if manual_status not in {"matched", "partial", "missing"}:
        raise ValueError(
            f"Invalid manual status for {requirement_id}: "
            f"{manual_status}"
        )

    resume_status = evaluation["status"]
    manual_confirmation = manual_record.get("confirmation")

    manual_items = []

    for item in manual_record.get("evidence", []):
        manual_items.append({
            **item,
            "evidence_source": "user_confirmed",
            "source_type": "manual_confirmation",
        })

    evaluation["resume_status"] = resume_status
    evaluation["manual_status"] = manual_status
    evaluation["manual_confirmation"] = manual_confirmation
    evaluation["manual_evidence"] = manual_items

    evidence_groups = evaluation.get("evidence_groups", [])

    if evidence_groups:
        groups_by_label = {
            group["label"]: group
            for group in evidence_groups
        }

        # Apply evidence only to the group explicitly identified.
        # Apply manual evidence only to its explicitly identified group.
                # Apply manual evidence only to its explicitly identified group.
        for item in manual_items:
            explicit_group_label = item.get("evidence_group")
            group_label = explicit_group_label

            # A single-group requirement can use its only group as a fallback.
            if not group_label and len(evidence_groups) == 1:
                group_label = evidence_groups[0]["label"]

            if not group_label:
                continue

            if group_label not in groups_by_label:
                raise ValueError(
                    f"Unknown evidence group '{group_label}' "
                    f"for {requirement_id}. "
                    f"Available groups: {list(groups_by_label)}"
                )

            group = groups_by_label[group_label]

            group.setdefault("manual_evidence", []).append(item)
            group["manual_evidence_count"] = len(
                group["manual_evidence"]
            )

            # Explicit group evidence satisfies that group.
            # Single-group fallback respects partial confirmation.
            if explicit_group_label:
                group["status"] = "matched"
                group["satisfied"] = True

            elif manual_status == "partial":
                group["status"] = "partial"
                group["satisfied"] = False

            else:
                group["status"] = "matched"
                group["satisfied"] = True

        # For a single-group requirement, a manual partial confirmation
        # can establish partial support even without a specific evidence item.
        if (
            len(evidence_groups) == 1
            and manual_status == "partial"
            and not evidence_groups[0].get("manual_evidence")
            and resume_status != "matched"
        ):
            evidence_groups[0]["status"] = "partial"
            evidence_groups[0]["satisfied"] = False

        matched_count = sum(
            group.get("status") == "matched"
            for group in evidence_groups
        )

        partial_count = sum(
            group.get("status") == "partial"
            for group in evidence_groups
        )

        total_groups = len(evidence_groups)

        if total_groups and matched_count == total_groups:
            evaluation["status"] = "matched"
            evaluation["status_reason"] = (
                "All configured evidence groups are supported "
                "by resume evidence or separately recorded "
                "user-confirmed evidence."
            )
            evaluation["evidence_strength"] = (
                "user_confirmed"
                if any(
                    group.get("manual_evidence")
                    for group in evidence_groups
                )
                else evaluation.get(
                    "evidence_strength",
                    "implementation",
                )
            )

        elif matched_count or partial_count:
            evaluation["status"] = "partial"
            evaluation["status_reason"] = (
                f"{matched_count} of {total_groups} configured "
                "evidence groups are fully supported. "
                "The remaining groups require further evidence."
            )
            evaluation["evidence_strength"] = "user_confirmed_partial"

        else:
            evaluation["status"] = resume_status

    else:
        # Preserve manual confirmation behavior for requirements
        # that do not use evidence groups.
        if manual_status == "matched":
            evaluation["status"] = "matched"
            evaluation["status_reason"] = (
                "Requirement supported by separately recorded "
                "user-confirmed evidence."
            )
            evaluation["evidence_strength"] = "user_confirmed"

        elif manual_status == "partial":
            if resume_status != "matched":
                evaluation["status"] = "partial"
                evaluation["status_reason"] = (
                    manual_confirmation
                    or "Partial support established through "
                       "user-confirmed evidence."
                )
                evaluation["evidence_strength"] = (
                    "user_confirmed_partial"
                )

        elif manual_status == "missing":
            evaluation["status"] = "missing"
            evaluation["status_reason"] = (
                manual_confirmation
                or "User confirmation established that the "
                   "required experience is not present."
            )
            evaluation["evidence_strength"] = "none"

    return evaluation

# ---------------------------------------------------------
# OUTPUT GENERATION
# ---------------------------------------------------------

def build_output(jd_data, resume_data, resume_type, manual_data):
    segments = build_resume_segments(resume_data)

    results = []

    for requirement in jd_data.get("requirements", []):
        evaluation = evaluate_requirement(requirement, segments)

        evaluation = apply_manual_evidence(
            evaluation,
            requirement.get("requirement_id"),
            manual_data,
        )

        results.append(evaluation)

    counts = {
        "matched": sum(
            item["status"] == "matched"
            for item in results
        ),
        "partial": sum(
            item["status"] == "partial"
            for item in results
        ),
        "missing": sum(
            item["status"] == "missing"
            for item in results
        ),
    }

    method_counts = {}

    for item in results:
        method = item["evaluation_method"]
        method_counts[method] = method_counts.get(method, 0) + 1

    return {
        "schema_version": "1.5",
        "matching_method": (
            "deterministic_resume_matching_with_user_confirmed_evidence"
        ),
        "dictionary_version": DICTIONARY_VERSION,
        "sources": {
            "jd_skill_tags_file": JD_TAGS_FILE.name,
            "resume_file": resume_data.get("source_file"),
            "resume_type": resume_type,
            "manual_evidence_file": MANUAL_EVIDENCE_FILE.name,
        },
        "summary": {
            "total_requirements": len(results),
            "matched": counts["matched"],
            "partial": counts["partial"],
            "missing": counts["missing"],
            "evaluation_methods": method_counts,
            "evidence_sources": [
                "resume_extracted",
                "user_confirmed",
            ],
            "evidence_policy": (
                "Resume evidence retains its original source text and "
                "segment-relative offsets. User-confirmed evidence is "
                "stored separately and is never represented as a resume "
                "quotation. Requirement status may use either source, "
                "with multi-part requirements retaining their evidence "
                "conditions."
            ),
        },
        "requirements": results,
    }


# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------

def main():
    try:
        if not JD_TAGS_FILE.is_file():
            raise FileNotFoundError(JD_TAGS_FILE)

        jd_data = load_json(JD_TAGS_FILE)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        manual_data = load_manual_evidence()

        for resume_type, resume_path in RESUME_FILES.items():
            if not resume_path.is_file():
                raise FileNotFoundError(resume_path)

            resume_data = load_json(resume_path)

            output = build_output(
                jd_data,
                resume_data,
                resume_type,
                manual_data,
            )
    
            output_path = (
                OUTPUT_DIR
                / f"ai_engineer_jd_{resume_type}_evidence_match.json"
            )

            with output_path.open("w", encoding="utf-8") as file:
                json.dump(
                    output,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            summary = output["summary"]

            print(f"\n{resume_type.upper()} RESUME")
            print("-" * 40)
            print(f"Requirements : {summary['total_requirements']}")
            print(f"Matched      : {summary['matched']}")
            print(f"Partial      : {summary['partial']}")
            print(f"Missing      : {summary['missing']}")
            print(f"Output       : {output_path.name}")

            print("\nEvaluation methods:")

            for method, count in summary["evaluation_methods"].items():
                print(f"  {method}: {count}")

        print("\nEVIDENCE MATCHING COMPLETE")

    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as error:
        print(f"ERROR: {type(error).__name__}: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
