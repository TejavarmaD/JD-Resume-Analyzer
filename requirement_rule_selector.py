"""Requirement-driven strategy selection.

Selection is based on the current requirement wording and extracted tags.
Requirement IDs are deliberately ignored.
"""
import re

RULE_PATTERNS = (
    ("education_evidence", r"\b(bachelor|b\.?tech|degree|academic qualification)\b"),
    ("explicit_experience_duration", r"\b(\d+\+?\s+years?|more than \w+ years?|at least \w+ years?)\b"),
    ("python_proficiency_evidence", r"\b(proficien(t|cy)|strong python|high proficiency)\b.*\bpython\b|\bpython\b.*\b(proficien(t|cy)|strong|advanced)\b"),
    ("model_api_integration_evidence", r"\b(api|apis|rest api|model api)\b.*\b(integrat|connect|implement|develop|build)\w*|\b(integrat|connect|implement|develop|build)\w*.*\b(api|apis)\b"),
    ("implemented_llm_use_case_evidence", r"\b(question.answer|information extraction|content generation|summari[sz]ation)\b"),
    ("explicit_llm_application_phrase_evidence", r"\b(built|developed) an? (working )?llm[- ]powered application\b|\b(llm[- ]powered|working llm) application\b"),
    ("working_llm_application_evidence", r"\b(llm|large language model)\b.{0,50}\b(application|app|solution)\b"),
    ("reliable_llm_feature_evidence", r"\b(reliab|robust|validat|ground|hallucination)\w*\b.{0,60}\b(llm|model|ai)\b|\b(llm|model|ai)\b.{0,60}\b(reliab|robust|validat|ground|hallucination)\w*\b"),
    ("python_code_quality_evidence", r"\b(modular|reusable|maintainable|clean code|software engineering best practices)\b"),
    ("evaluation_evidence", r"\b(llm evaluation|model evaluation|response relevance|factual accuracy|retrieval accuracy|grounded responses)\b"),
    ("evaluation_testing_evidence", r"\b(evaluat|test|benchmark|regression)\w*\b.{0,60}\b(ai|llm|model|agent)\b|\b(ai|llm|model|agent)\b.{0,60}\b(evaluat|test|benchmark|regression)\w*\b"),
    ("deployment_monitoring_evidence", r"\b(deploy|production)\w*\b.{0,60}\b(monitor|logging|performance)\w*\b|\b(monitor|logging|performance)\w*\b.{0,60}\b(deploy|production|application)\w*\b"),
    ("workflow_design_evidence", r"\b(deterministic|rule.based)\b.{0,60}\b(workflow|process|agent)\b|\b(human.in.the.loop|agent autonomy)\b"),
    ("agentic_workflow_evidence", r"\b(agentic|ai agents?|autonomous agents?|agent workflows?)\b"),
    ("feature_ownership_evidence", r"\b(develop|build|test|deploy)\w*.*\b(end.to.end|lifecycle|feature)\b|\b(end.to.end|feature lifecycle)\b"),
    ("business_problem_translation_evidence", r"\b(business need|business problem|business requirement|business users)\b"),
    ("analytical_problem_solving_evidence", r"\b(root cause|problem.solving|investigat|reconcil)\w*\b"),
    ("technical_communication_evidence", r"\b(technical documentation|technical discussions|knowledge transfer|code reviews|present technical)\b"),
    ("collaboration_evidence", r"\b(engineering teams?|product teams?|cross.functional teams?)\b"),
    ("communication_collaboration_evidence", r"\b(communicat|collaborat|cross.functional|stakeholder)\w*\b"),
    ("learning_adaptability_evidence", r"\b(continuous learning|self.directed learning|upskill|adaptab|learn new technologies)\b"),
)

def select_requirement_strategy(requirement):
    """Return a strategy key and explainable selection metadata."""
    text = str(requirement.get("requirement_text") or "")
    folded = text.casefold()
    tags = set()
    for category in ("concepts", "technologies", "platforms", "standards"):
        for item in (requirement.get("skill_tags") or {}).get(category, []):
            if isinstance(item, dict) and item.get("tag"):
                tags.add(str(item["tag"]).casefold())

    # Strong tag signals supplement wording; they never use the requirement ID.
    if "python" in tags and re.search(r"\b(proficien|strong|advanced)\b", folded):
        return {"strategy": "python_proficiency_evidence", "matched_by": "wording_and_tags"}
    if "api" in tags and tags.intersection({"openai", "azure_openai", "anthropic", "google_gemini"}):
        if re.search(r"\b(api|integrat|connect)\w*\b", folded):
            return {"strategy": "model_api_integration_evidence", "matched_by": "wording_and_tags"}
    if tags.intersection({"question_answering", "information_extraction", "content_generation"}):
        if re.search(r"\b(llm|language model|generat|extract|question.answer)\w*\b", folded):
            return {"strategy": "implemented_llm_use_case_evidence", "matched_by": "wording_and_tags"}

    for strategy, pattern in RULE_PATTERNS:
        if re.search(pattern, folded, re.IGNORECASE):
            return {"strategy": strategy, "matched_by": "requirement_wording"}
    return {"strategy": "generic_requirement_evidence_matching", "matched_by": "generic_fallback"}
