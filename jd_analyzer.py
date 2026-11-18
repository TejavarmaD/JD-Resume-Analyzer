from pathlib import Path
import json
import re
import sys
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_JD_FILE = BASE_DIR / "jd_inputs" / "ai_engineer_jd.txt"
OUTPUT_DIR = BASE_DIR / "jd_results"



# ============================================================
# 1. ROLE-AGNOSTIC CATEGORY RULES
# ============================================================



CATEGORY_RULES = {
    "software_engineering": [
        "software engineering", "software development",
        "backend development", "backend services",
        "rest api", "rest apis", "api development",
        "application programming interface",
        "object-oriented programming", "modular code",
        "unit testing", "software architecture",
        "programming fundamentals", "programming languages",
        "fastapi", "flask", "python",
        "code reviews", "technical discussions",
        "technical documentation",
        "integrate ai applications", "enterprise systems",
        "external services", "database integration",
        "third-party integrations",
    ],

    "data_analytics": [
        "data analysis", "data analytics",
        "analyze datasets", "analyze data",
        "statistical analysis", "data visualization",
        "power bi", "tableau", "excel", "sql",
        "dashboards", "reporting",
        "business intelligence", "data interpretation",
        "data insights", "data exploration",
    ],

    "data_engineering": [
        "data engineering", "data pipelines",
        "etl pipelines", "etl", "elt",
        "data warehouse", "data warehouses",
        "data infrastructure", "data ingestion",
        "data integration", "data transformation",
        "data orchestration", "database administration",
        "data lakes", "database systems",
    ],

    "artificial_intelligence": [
        "artificial intelligence", "machine learning",
        "deep learning", "neural networks",
        "predictive modeling", "predictive modelling",
        "model training", "model inference",
        "computer vision", "natural language processing",
        "reinforcement learning", "classification models",
        "practical ai solutions", "ai-powered solutions",
        "ai solutions", "ai workflows",
        "business problems into",
    ],

    "generative_ai_llm": [
        "generative ai", "large language models",
        "large language model", "llm", "llms",
        "llm-powered", "llm application", "llm applications",
        "llm api", "llm apis",
        "prompt engineering", "prompt templates",
        "prompt optimization", "structured outputs",
        "context windows", "context management",
        "function calling", "transformers",
        "fine-tuning", "hugging face",
        "openai", "anthropic claude", "google gemini",
        "azure openai", "multimodal ai",
        "document intelligence", "question answering",
        "information extraction", "content generation",
        "open-source models", "open source models",
        "open-source language models",
        "open source language models",
        "llama", "mistral", "qwen",
    ],

    "retrieval_information_systems": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag", "vector database", "vector databases",
        "vector db", "vector retrieval", "vector search",
        "semantic search", "hybrid search",
        "document ingestion", "document retrieval",
        "document chunking", "embeddings",
        "embedding models", "reranking",
        "information retrieval",
        "faiss", "chroma", "pinecone",
        "qdrant", "pgvector",
    ],

    "agentic_systems": [
        "agentic ai", "ai agents", "agent frameworks",
        "agentic workflows", "workflow orchestration",
        "execution orchestration",
        "multi-step tasks", "multi-step execution",
        "task planning", "tool calling",
        "human-in-the-loop", "human in the loop",
        "approval checkpoints", "autonomous agents",
        "autonomous agent",
        "openai agents sdk", "langgraph", "crewai",
        "model context protocol", "mcp",
        "agent tools", "agent integrations",
        "agent tool integrations",
        "agent workflow automation",
        "third-party platforms", "internal services",
    ],

    "cloud_devops": [
        "cloud computing", "cloud platforms",
        "cloud infrastructure", "application deployment",
        "application hosting", "deployment",
        "continuous integration", "continuous deployment",
        "ci/cd", "devops", "docker", "kubernetes",
        "aws", "azure", "gcp",
    ],

    "evaluation_reliability": [
        "software testing", "automated testing",
        "unit testing", "integration testing",
        "test cases", "quality assurance",
        "model evaluation", "llm evaluation",
        "retrieval evaluation", "agent evaluation",
        "evaluation metrics", "response quality",
        "hallucination detection", "factual accuracy",
        "observability", "tracing", "logging",
        "monitoring", "failure handling",
        "langsmith", "langfuse", "ragas",
        "latency measurement", "hallucinations",
        "groundedness", "repeatable evaluation",
        "evaluation and testing practices",
    ],

    "security_responsible_practices": [
        "data privacy", "privacy protection",
        "information security", "cybersecurity",
        "access control", "authentication",
        "authorization", "input validation",
        "prompt injection", "security risks",
        "responsible ai", "ai governance",
        "privacy compliance", "security safeguards",
    ],

    "product_management": [
        "product management", "product strategy",
        "product roadmap", "product vision",
        "feature prioritization", "prioritize features",
        "product requirements", "product lifecycle",
        "product discovery", "product development",
        "market research", "user stories",
        "product backlog",
    ],

    "project_management": [
        "project management", "project planning",
        "project timelines", "project delivery",
        "delivery coordination", "project milestones",
        "project schedules", "resource planning",
        "project tracking", "risk management",
        "project execution",
    ],

    "business_operations": [
        "business operations", "business processes",
        "process improvement", "operational efficiency",
        "process optimization", "operational excellence",
        "workflow improvement",
    ],

    "design": [
        "user experience", "user interface",
        "ux design", "ui design",
        "ux research", "user research",
        "wireframes", "prototyping",
        "interaction design", "visual design",
        "design systems", "usability testing",
    ],

    "finance": [
        "financial analysis", "financial reporting",
        "financial forecasts", "financial forecasting",
        "financial planning", "financial modelling",
        "financial modeling", "budgeting", "budgets",
        "accounting", "cash flow",
        "financial statements", "variance analysis",
    ],

    "professional_skills": [
        "communication", "collaboration",
        "interpersonal skills", "conflict resolution",
        "negotiation", "adaptability", "teamwork",
        "active listening", "leadership",
        "problem-solving", "analytical thinking",
        "critical thinking", "stakeholder management",
        "cross-functional teams", "cross-functional",
        "work independently", "decision-making",
        "willingness to learn", "adapt to",
        "learning agility", "collaborate with",
        "work closely with", "business stakeholders",
        "engineering teams", "product teams",
        "feature ownership", "end-to-end ownership",
        "take ownership", "ownership of features",
        "own features",
    ],

    "qualifications_experience": [
        "bachelor's degree", "bachelors degree",
        "master's degree", "masters degree",
        "associate degree", "doctorate", "phd",
        "academic qualification", "certification",
        "professional certification", "license",
        "equivalent practical experience",
        "hands-on experience", "demonstrable experience",
        "practical experience", "relevant professional experience",
        "minimum 2 years", "relevant experience",
        "years of experience",
    ],
}


# ============================================================
# 2. CATEGORY AND PRIORITY WEIGHTS
# ============================================================

# Professional domain does not influence requirement importance.
DEFAULT_CATEGORY_WEIGHT = 1.0

PRIORITY_WEIGHTS = {
    "must_have": 1.0,
    "good_to_have": 0.5,
    "context": 0.0,
}


GOOD_TO_HAVE_SECTION = "good_to_have"


# ============================================================
# 3. JD SECTION HEADINGS
# ============================================================

SECTION_HEADINGS = {
    "about the role",

    # General requirement and responsibility headings
    "core requirements",
    "requirements",
    "key responsibilities",
    "roles and responsibilities",

    # General JD sections
    "role summary",
    "required qualifications",
    "preferred qualifications",
    "technical stack summary",
    "responsibilities",
    "qualifications",
    "minimum qualifications",
    "preferred experience",
    "nice to have",
    "technical skills",
    "what you'll do",
    "what you will do",
    "what we're looking for",
    "what we are looking for",

    # Existing technical sections
    "generative ai and llm application development",
    "retrieval-augmented generation (rag)",
    "agentic ai and workflow automation",
    "backend engineering and api development",
    "ai evaluation, testing and reliability",
    "deployment and collaboration",
    "required technical skills",
    "programming and backend",
    "generative ai and llms",
    "rag and vector databases",
    "agentic ai",
    "cloud and deployment",
    "experience and education",
    "good to have",
    "what we expect",
    "expected outcomes",
}


# ============================================================
# 4. TEXT CLEANING
# ============================================================

def clean_line(line: str) -> str:
    """Remove formatting artifacts without changing meaning."""

    line = line.strip()
    line = line.rstrip("\\").strip()
    line = re.sub(r"^#{1,6}\s*", "", line)
    line = line.replace("**", "")

    return line.strip()


def is_heading(line: str) -> bool:
    """Identify recognized JD section headings."""

    normalized = line.strip().casefold()

    normalized = re.sub(
        r"^\d+[.)]\s*",
        "",
        normalized,
    )

    normalized = normalized.rstrip(":")

    return normalized in SECTION_HEADINGS


def remove_list_marker(line: str) -> str:
    """Remove bullet and numbered-list prefixes."""

    line = re.sub(r"^\s*[-*•▪◦]\s*", "", line)
    line = re.sub(r"^\s*\d+[.)]\s*", "", line)

    return line.strip()


# ============================================================
# 5. CATEGORY DETECTION
# ============================================================



def detect_category(
    text: str,
    section: str = "",
) -> str:
    """
    Classify a requirement using transparent keyword matching.

    Requirement text is the primary evidence.
    Source section provides supplementary evidence.

    Specific phrases receive more weight than single words.
    Ambiguous or equally supported categories return "general".

    Categories do not affect requirement scoring.
    """

    normalized_text = re.sub(
        r"\s+",
        " ",
        text.casefold(),
    ).strip()

    normalized_section = re.sub(
        r"\s+",
        " ",
        (section or "").casefold(),
    ).strip()

    category_scores = {}

    for category, keywords in CATEGORY_RULES.items():

        text_matches = [
            keyword
            for keyword in keywords
            if re.search(
                r"(?<!\w)"
                + re.escape(keyword.casefold())
                + r"(?!\w)",
                normalized_text,
            )
        ]

        # Multi-word phrases are more specific than single words.
        text_score = sum(
            2 if " " in keyword else 1
            for keyword in text_matches
        )

        # Section headings can support a category,
        # but cannot classify a requirement by themselves.
        section_matches = [
            keyword
            for keyword in keywords
            if re.search(
                r"(?<!\w)"
                + re.escape(keyword.casefold())
                + r"(?!\w)",
                normalized_section,
            )
        ]

        section_score = (
            1 if text_score > 0 and section_matches else 0
        )

        category_scores[category] = (
            text_score + section_score
        )

    if not category_scores:
        return "general"

    ranked_categories = sorted(
        category_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    highest_category, highest_score = ranked_categories[0]

    if highest_score == 0:
        return "general"

    # Equally supported categories are ambiguous.
    if (
        len(ranked_categories) > 1
        and ranked_categories[0][1] == ranked_categories[1][1]
    ):
        return "general"

    return highest_category



# ============================================================
# 6. PRIORITY DETECTION
# ============================================================


def detect_priority(section: str) -> str:
    """Classify requirements based on their source section."""

    normalized_section = re.sub(
        r"[\s-]+",
        "_",
        section.strip().casefold(),
    )

    good_to_have_sections = {
        GOOD_TO_HAVE_SECTION,
        "preferred_qualifications",
        "preferred_experience",
        "nice_to_have",
        "desirable_qualifications",
        "desirable_experience",
    }

    if normalized_section in good_to_have_sections:
        return "good_to_have"

    return "must_have"



# ============================================================
# 7. REQUIREMENT TYPE CLASSIFICATION
# ============================================================



def classify_requirement_type(
    text: str,
    category: str,
    section: str,
) -> str:
    """
    Classify a JD requirement independently of its professional domain.

    Categories describe the subject area. Requirement types describe
    what the employer expects from the candidate.
    """

    normalized_text = re.sub(
        r"\s+",
        " ",
        text.casefold(),
    ).strip()

    normalized_section = re.sub(
        r"[_\-]+",
        " ",
        section.casefold(),
    ).strip()

    # 1. Qualifications: education, certifications and demonstrable
    # experience requirements.
    qualification_patterns = [
        r"\b\d+\+?\s+years?\b",
        r"\b(?:bachelor|master|doctorate|phd|associate)(?:'s)?\s+degree\b",
        r"\bdegree\s+in\b",
        r"\bcertifications?\b",
        r"\blicen[cs]e(?:d)?\b",
        r"\bminimum qualifications?\b",
        r"\bequivalent practical experience\b",
        r"\b(?:demonstrable|proven|practical|hands-on)\s+experience\b",
        r"\bexperience\s+(?:developing|implementing|building|"
        r"integrating|managing|leading|designing|delivering)\b",
        r"\bexperience of\s+(?:developing|implementing|building|"
        r"integrating|managing|leading|designing|delivering)\b",
    ]

    if any(
        re.search(pattern, normalized_text)
        for pattern in qualification_patterns
    ):
        return "qualification"

    # 2. Outcomes: preserve explicit outcome-section context.
    if normalized_section == "expected outcomes":
        return "outcome"

    # 3. Behavioral and interpersonal competencies.
    soft_skill_patterns = [
        r"\bcommunication\b",
        r"\bcollaboration\b",
        r"\bproblem[\s-]solving\b",
        r"\banalytical thinking\b",
        r"\bcritical thinking\b",
        r"\bownership\b",
        r"\binitiative\b",
        r"\badaptability\b",
        r"\bresilience\b",
        r"\bwillingness to learn\b",
        r"\binterpersonal skills?\b",
        r"\bstakeholder management\b",
        r"\bcross[\s-]functional\b",
        r"\bnegotiation\b",
        r"\bconflict resolution\b",
        r"\bdecision[\s-]making\b",
        r"\bability to (?:communicate|collaborate|influence|"
        r"lead|adapt|work independently)\b",
        r"\bconvert business problems into\b",
    ]

    if any(
        re.search(pattern, normalized_text)
        for pattern in soft_skill_patterns
    ):
        return "soft_skill"

    # 4. Responsibilities: action-oriented work expectations.
    responsibility_patterns = [
        r"^\s*(?:"
        r"analy[sz]e|assess|audit|automate|"
        r"build|calculate|collaborate|communicate|"
        r"conduct|configure|coordinate|create|"
        r"define|deliver|deploy|design|develop|"
        r"drive|document|"
        r"establish|evaluate|execute|"
        r"facilitate|"
        r"generate|"
        r"identify|implement|improve|integrate|"
        r"investigate|"
        r"lead|maintain|manage|measure|monitor|"
        r""
        r"optimize|organize|"
        r"participate|plan|prepare|present|produce|"
        r""
        r"recommend|research|resolve|review|"
        r""
        r"support|"
        r"test|track|train|translate|troubleshoot|"
        r""
        r"validate|"
        r"write"
        r")\b",
        r"^\s*work\s+with\s+"
        r"(?:stakeholders|clients|customers|teams|"
        r"colleagues|partners|vendors|leadership)\b",
        r"^\s*be\s+responsible\s+for\b",
        r"^\s*take\s+responsibility\s+for\b",
        r"^\s*own\s+and\s+(?:manage|deliver|drive|lead)\b",
        r"^\s*ensure\s+",
        r"^\s*contribute\s+to\b",
        r"^\s*understand\s+when\b",
    ]

    if any(
        re.search(pattern, normalized_text)
        for pattern in responsibility_patterns
    ):
        return "responsibility"

    # Handle action-oriented statements in responsibility sections.
    if (
        normalized_section in {
            "key responsibilities",
            "roles and responsibilities",
            "responsibilities",
        }
        and re.match(
            r"^\s*(?:use|understand when)\b",
            normalized_text,
        )
    ):
        return "responsibility"

    # 5. Remaining statements describe skills, knowledge,
    # tools, methods or capabilities.
    return "skill"


# ============================================================
# 8. WEIGHT CALCULATION
# ============================================================

def calculate_weight(category: str, priority: str) -> float:
    """
    Calculate requirement importance from JD priority only.

    Category is retained in the signature for compatibility,
    but it does not influence the weight.
    """

    priority_weight = PRIORITY_WEIGHTS.get(priority, 0.0)

    return round(priority_weight, 2)


# ============================================================
# 9. REQUIREMENT EXTRACTION
# ============================================================


# Sections whose content should be evaluated as requirements.
REQUIREMENT_SECTIONS = {
    "about the role",
    "core requirements",
    "requirements",
    "key responsibilities",
    "roles and responsibilities",
    "responsibilities",
    "required qualifications",
    "preferred qualifications",
    "minimum qualifications",
    "preferred experience",
    "nice to have",
    "qualifications",
    "what you'll do",
    "what you will do",
    "what we're looking for",
    "what we are looking for",

    # Existing technical sections
    "generative ai and llm application development",
    "retrieval-augmented generation (rag)",
    "agentic ai and workflow automation",
    "backend engineering and api development",
    "ai evaluation, testing and reliability",
    "deployment and collaboration",
    "required technical skills",
    "programming and backend",
    "generative ai and llms",
    "rag and vector databases",
    "agentic ai",
    "cloud and deployment",
    "experience and education",
    "what we expect",
    "expected outcomes",
}

CONTEXT_ONLY_SECTIONS = {
    "role summary",
    "technical stack summary",
}


def is_list_item(line: str) -> bool:
    """Identify bullet and numbered requirement lines."""

    return bool(
        re.match(
            r"^\s*([-*•▪◦]|\d+[.)])\s*",
            line,
        )
    )


def is_subsection_heading(line: str, section: str) -> bool:
    """
    Identify short nested headings inside responsibility sections.

    Examples:
    Multimodal RAG & Knowledge Systems
    AI Agents & Web Automation
    Backend & Cloud Architecture
    """

    if section not in {
        "key responsibilities",
        "roles and responsibilities",
        "responsibilities",
    }:
        return False

    text = line.strip()

    if not text or is_list_item(text):
        return False

    # Inline labels such as "Experience: 2+ years..."
    # must remain requirement content.
    if ":" in text:
        return False

    # A sentence is not a subsection heading.
    if re.search(r"[.!?;]$", text):
        return False

    words = text.split()

    if len(words) > 9 or len(text) > 90:
        return False

    # Require title-like formatting or an explicit ampersand.
    title_like = (
        text == text.title()
        or "&" in text
    )

    return title_like





def extract_requirements(jd_text: str) -> list[dict]:
    """
    Extract requirements from bullets, numbered items, and paragraphs.

    Extraction does not depend on a predefined section-heading list.
    Consecutive physical lines are joined into logical paragraphs.
    """

    requirements = []
    current_section = ""
    current_subsection = ""
    seen = set()
    pending_lines = []

    metadata_pattern = re.compile(
        r"^(job description|job title|experience|location|employment type|"
        r"department|seniority)\s*:",
        re.IGNORECASE,
    )

    metadata_fields = {
    "job description",
    "job title",
    "experience",
    "location",
    "employment type",
    "department",
    "seniority",
    }

    context_intro_pattern = re.compile(
        r"^(?:"
        r"(?:within|in) the first \d+\s+months?,\s+"
        r"(?:the\s+)?(?:engineer|candidate)\s+"
        r"(?:is|are)\s+expected\s+to:"
        r"|you will be responsible for:"
        r"|the successful candidate will:"
        r"|the ideal candidate will:"
        r"|key responsibilities include:"
        r"|the following responsibilities:"
        r")$",
        re.IGNORECASE,
    )

    def add_requirement(
        requirement_text: str,
        section: str = None,
        subsection: str = None,
    ):
        requirement_text = requirement_text.strip()

        if len(requirement_text) < 8:
            return

        if context_intro_pattern.match(requirement_text):
            return

        deduplication_key = re.sub(
            r"\s+",
            " ",
            requirement_text.casefold(),
        )

        if deduplication_key in seen:
            return

        seen.add(deduplication_key)

        source_section_name = (
            current_section if section is None else section
        )
        source_subsection_name = (
            current_subsection if subsection is None else subsection
        )

        category = detect_category(
            requirement_text,
            source_section_name,
        )

        priority = detect_priority(source_section_name)

        requirement_type = classify_requirement_type(
            requirement_text,
            category,
            source_section_name,
        )

        source_section = source_section_name

        if source_subsection_name:
            source_section = (
                f"{source_section_name} / {source_subsection_name}"
                if source_section_name
                else source_subsection_name
            )

        requirements.append({
            "id": f"REQ-{len(requirements) + 1:03d}",
            "requirement": requirement_text,
            "category": category,
            "priority": priority,
            "requirement_type": requirement_type,
            "category_weight": DEFAULT_CATEGORY_WEIGHT,
            "priority_weight": PRIORITY_WEIGHTS[priority],
            "base_weight": calculate_weight(
                category,
                priority,
            ),
            "source_section": source_section,
            "source_evidence": requirement_text,
        })

    def flush_paragraph():
        if not pending_lines:
            return

        paragraph = " ".join(pending_lines).strip()
        pending_lines.clear()

        if not paragraph:
            return

        if current_section in CONTEXT_ONLY_SECTIONS:
            return

        add_requirement(paragraph)

    def detect_unknown_heading(line: str) -> bool:
        """
        Recognize likely standalone headings without requiring
        them to exist in SECTION_HEADINGS.

        This is intentionally conservative to avoid treating
        ordinary sentences as headings.
        """

        text = line.strip()

        if not text or is_list_item(text):
            return False

        if len(text) > 90:
            return False

        if text.endswith((".", "!", "?", ";")):
            return False

        if ":" in text:
            return False

        words = text.split()

        if len(words) > 9:
            return False

        if is_heading(text):
            return True

        # Short title-case headings, including contractions.
        # Examples: "Your Profile", "What You'll Bring",
        # "Who We're Looking For".
        words = re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", text)
        if words and all(
            word[0].isupper()
            for word in words
        ):
            return True

        # Short headings written in uppercase.
        if text.isupper() and any(char.isalpha() for char in text):
            return True

        return False

    def normalize_section(line: str) -> str:
        return re.sub(
            r"^\d+[.)]\s*",
            "",
            line.strip(),
        ).casefold().rstrip(":")

    for raw_line in jd_text.splitlines():

        line = clean_line(raw_line)

        if not line:
            flush_paragraph()
            continue

        # Recognized headings always take precedence.
        if is_heading(line):
            flush_paragraph()

            current_section = normalize_section(line)
            current_subsection = ""
            continue

        # Metadata fields are not candidate requirements.
        metadata_match = metadata_pattern.match(line)

        if metadata_match:
            flush_paragraph()

            field_name = metadata_match.group(1).casefold()

            # Do not treat ordinary qualification labels as metadata.
            if field_name in metadata_fields:
                continue

        if current_section in CONTEXT_ONLY_SECTIONS:
            continue

        # Bullets and numbered items are independent requirements.
        if is_list_item(line):
            flush_paragraph()

            add_requirement(
                remove_list_marker(line)
            )
            continue

        # Nested subsection headings in responsibility sections.
        if (
            not pending_lines
            and is_subsection_heading(line, current_section)
        ):
            current_subsection = line.strip()
            continue

        # Detect unfamiliar standalone headings.
        if (
            not pending_lines
            and detect_unknown_heading(line)
        ):
            flush_paragraph()

            current_section = normalize_section(line)
            current_subsection = ""
            continue

        # A completed sentence on the previous physical line
        # indicates a new requirement when another line follows.
        if pending_lines:
            previous_line = pending_lines[-1].strip()

            if re.search(r"[.!?][\"')\]]?$", previous_line):
                flush_paragraph()

        # Qualification labels start separate logical requirements.
        if (
            pending_lines
            and re.match(
                r"^[A-Za-z][A-Za-z &/()-]{1,40}:\s+\S",
                line,
            )
        ):
            flush_paragraph()
        pending_lines.append(line)

    flush_paragraph()

    return requirements


# ============================================================
# 10. JOB METADATA EXTRACTION
# ============================================================

def extract_metadata(jd_text: str) -> dict:

    metadata = {}

    patterns = {
        "job_title": r"Job Title\s*:\s*(.+)",
        "experience": r"Experience\s*:\s*(.+)",
        "location": r"Location\s*:\s*(.+)",
        "employment_type": r"Employment Type\s*:\s*(.+)",
        "department": r"Department\s*:\s*(.+)",
        "seniority": r"Seniority\s*:\s*(.+)",
    }

    for field, pattern in patterns.items():

        match = re.search(
            pattern,
            jd_text,
            re.IGNORECASE,
        )

        metadata[field] = (
            clean_line(match.group(1))
            if match
            else None
        )

    return metadata


# ============================================================
# 11. CATEGORY SUMMARY
# ============================================================

def build_category_summary(requirements: list[dict]) -> dict:

    summary = {}

    for requirement in requirements:

        category = requirement["category"]

        if category not in summary:
            summary[category] = {
                "total": 0,
                "must_have": 0,
                "good_to_have": 0,
            }

        summary[category]["total"] += 1

        summary[category][requirement["priority"]] += 1

    return summary


# ============================================================
# 12. COMPLETE JD ANALYSIS
# ============================================================

def analyze_jd(jd_text: str) -> dict:

    requirements = extract_requirements(jd_text)

    must_have_count = sum(
        item["priority"] == "must_have"
        for item in requirements
    )

    good_to_have_count = sum(
        item["priority"] == "good_to_have"
        for item in requirements
    )

    requirement_type_summary = {}

    for item in requirements:

        requirement_type = item["requirement_type"]

        requirement_type_summary[requirement_type] = (
            requirement_type_summary.get(
                requirement_type,
                0,
            ) + 1
        )

    return {
        "schema_version": "1.0",
        "analysis_type": "rule_based_jd_analysis",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "job_metadata": extract_metadata(jd_text),

        "summary": {
            "total_requirements": len(requirements),
            "must_have_count": must_have_count,
            "good_to_have_count": good_to_have_count,
            "category_count": len(
                set(
                    item["category"]
                    for item in requirements
                )
            ),
            "requirement_type_summary": (
                requirement_type_summary
            ),
        },

        "category_summary": build_category_summary(
            requirements
        ),

        "requirements": requirements,

        "source": {
            "original_character_count": len(jd_text),
            "original_jd_text": jd_text,
        },

        "limitations": [
            "Category assignment uses keyword rules and may require review.",
            "Priority is inferred from the JD section, not from semantic importance.",
            "Requirement type classification uses transparent rule-based checks.",
            "Weights are initial design values and must be calibrated.",
            "No resume matching or candidate scoring is performed.",
        ],
    }


# ============================================================
# 13. MAIN EXECUTION
# ============================================================

def main() -> int:

    jd_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JD_FILE
    )

    if not jd_file.is_absolute():
        jd_file = BASE_DIR / jd_file

    if not jd_file.is_file():

        print(
            f"ERROR: JD file not found: {jd_file}"
        )

        return 1

    try:

        jd_text = jd_file.read_text(
            encoding="utf-8-sig"
        )

        if not jd_text.strip():

            print("ERROR: JD file is empty.")

            return 1

        result = analyze_jd(jd_text)

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            OUTPUT_DIR
            / f"{jd_file.stem}_analysis.json"
        )

        output_file.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print("\nJD ANALYSIS COMPLETE")
        print("--------------------")

        print(f"Input: {jd_file.name}")

        print(
            f"Job title: "
            f"{result['job_metadata']['job_title']}"
        )

        print(
            "Total requirements: "
            f"{result['summary']['total_requirements']}"
        )

        print(
            "Must-have: "
            f"{result['summary']['must_have_count']}"
        )

        print(
            "Good-to-have: "
            f"{result['summary']['good_to_have_count']}"
        )

        print("\nCategory breakdown:")

        for category, counts in (
            result["category_summary"].items()
        ):

            print(
                f"  {category}: {counts['total']} "
                f"(must-have: {counts['must_have']}, "
                f"good-to-have: {counts['good_to_have']})"
            )

        print("\nRequirement type breakdown:")

        for requirement_type, count in (
            result["summary"][
                "requirement_type_summary"
            ].items()
        ):

            print(
                f"  {requirement_type}: {count}"
            )

        print(f"\nJSON output:\n{output_file}")

        return 0

    except (
        OSError,
        UnicodeError,
        ValueError,
    ) as error:

        print(
            f"ERROR: JD analysis failed: "
            f"{type(error).__name__}: {error}"
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
