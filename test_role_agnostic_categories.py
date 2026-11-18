
import unittest

from jd_analyzer import detect_category


class TestRoleAgnosticCategories(unittest.TestCase):

    def test_detects_software_engineering(self):
        self.assertEqual(
            detect_category(
                "Develop REST APIs and maintain backend services."
            ),
            "software_engineering",
        )

    def test_detects_data_analytics(self):
        self.assertEqual(
            detect_category(
                "Analyze datasets using SQL and build Power BI dashboards."
            ),
            "data_analytics",
        )

    def test_detects_data_engineering(self):
        self.assertEqual(
            detect_category(
                "Build ETL pipelines and maintain data warehouses."
            ),
            "data_engineering",
        )

    def test_detects_product_management(self):
        self.assertEqual(
            detect_category(
                "Define product strategy, manage the roadmap, and prioritize features."
            ),
            "product_management",
        )

    def test_detects_project_management(self):
        self.assertEqual(
            detect_category(
                "Manage project timelines, coordinate delivery, and track milestones."
            ),
            "project_management",
        )

    def test_detects_business_operations(self):
        self.assertEqual(
            detect_category(
                "Improve business processes and operational efficiency."
            ),
            "business_operations",
        )

    def test_detects_design(self):
        self.assertEqual(
            detect_category(
                "Conduct user research and create UX wireframes."
            ),
            "design",
        )

    def test_detects_finance(self):
        self.assertEqual(
            detect_category(
                "Prepare financial forecasts, budgets, and financial reports."
            ),
            "finance",
        )

    def test_detects_professional_skills(self):
        self.assertEqual(
            detect_category(
                "Demonstrate strong communication and collaboration skills."
            ),
            "professional_skills",
        )

    def test_unknown_domain_returns_general(self):
        self.assertEqual(
            detect_category(
                "Maintain specialized laboratory instrumentation."
            ),
            "general",
        )


def test_classifies_python_as_software_engineering():
    assert detect_category("Strong proficiency in Python.") == "software_engineering"


def test_classifies_llm_use_cases_as_generative_ai():
    assert detect_category(
        "Implement question answering, information extraction and content generation."
    ) == "generative_ai_llm"


def test_classifies_hallucination_measurement_as_evaluation():
    assert detect_category(
        "Measure hallucinations, relevance and groundedness."
    ) == "evaluation_reliability"


def test_classifies_autonomous_agent_as_agentic_systems():
    assert detect_category(
        "Understand when an autonomous agent is appropriate."
    ) == "agentic_systems"


def test_classifies_relevant_experience_as_qualification():
    assert detect_category(
        "Minimum 2 years of relevant professional experience."
    ) == "qualifications_experience"


def test_classifies_learning_agility_as_professional_skill():
    assert detect_category(
        "A willingness to learn and adapt to new technologies."
    ) == "professional_skills"


def test_classifies_model_context_protocol_as_agentic_systems():
    assert detect_category(
        "Familiarity with Model Context Protocol (MCP)."
    ) == "agentic_systems"


def test_classifies_repeatable_evaluation_as_evaluation():
    assert detect_category(
        "Establish repeatable evaluation and testing practices."
    ) == "evaluation_reliability"


def test_equal_category_scores_return_general():
    assert detect_category(
        "Experience in software engineering and product strategy."
    ) == "general"


def test_higher_category_score_wins_with_one_point_margin():
    assert detect_category(
        "Develop REST APIs and use SQL."
    ) == "software_engineering"


if __name__ == "__main__":
    unittest.main()
