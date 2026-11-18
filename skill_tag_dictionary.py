"""
Controlled dictionary for deterministic JD skill tagging.

Version: 1.1

Policy:
- Explicit mentions only.
- Case-insensitive exact phrase matching.
- Longer phrases take precedence over shorter overlapping phrases.
- No fuzzy matching or automatic skill inference.
"""

DICTIONARY_VERSION = "1.1"

SKILL_DICTIONARY = {

    # ---------------------------------------------------------
    # CONCEPTS
    # ---------------------------------------------------------

    "llm": {
        "display_name": "Large Language Models",
        "category": "concepts",
        "aliases": [
            "large language models", "large language model",
            "llms", "llm",
        ],
    },
    "generative_ai": {
        "display_name": "Generative AI",
        "category": "concepts",
        "aliases": [
            "generative artificial intelligence", "generative ai",
        ],
    },
    "prompt_engineering": {
        "display_name": "Prompt Engineering",
        "category": "concepts",
        "aliases": [
            "prompt engineering", "prompt design",
            "prompting techniques",
        ],
    },
    "structured_output": {
        "display_name": "Structured Output",
        "category": "concepts",
        "aliases": [
            "structured outputs", "structured output",
        ],
    },
    "function_calling": {
        "display_name": "Function Calling",
        "category": "concepts",
        "aliases": [
            "function calling", "function calls",
        ],
    },
    "context_management": {
        "display_name": "Context Management",
        "category": "concepts",
        "aliases": [
            "context management", "context-management",
            "context window management",
        ],
    },
    "summarization": {
        "display_name": "Summarization",
        "category": "concepts",
        "aliases": [
            "text summarization", "summarization",
        ],
    },
    "question_answering": {
        "display_name": "Question Answering",
        "category": "concepts",
        "aliases": [
            "question answering", "question-answering",
        ],
    },
    "information_extraction": {
        "display_name": "Information Extraction",
        "category": "concepts",
        "aliases": [
            "information extraction", "data extraction",
        ],
    },
    "content_generation": {
        "display_name": "Content Generation",
        "category": "concepts",
        "aliases": ["content generation"],
    },
    "rag": {
        "display_name": "Retrieval-Augmented Generation",
        "category": "concepts",
        "aliases": [
            "retrieval-augmented generation",
            "retrieval augmented generation",
            "rag",
        ],
    },
    "document_parsing": {
        "display_name": "Document Parsing",
        "category": "concepts",
        "aliases": [
            "document parsing", "document ingestion",
            "document processing",
        ],
    },
    "chunking": {
        "display_name": "Document Chunking",
        "category": "concepts",
        "aliases": [
            "text chunking", "document chunking", "chunking",
        ],
    },
    "embeddings": {
        "display_name": "Embeddings",
        "category": "concepts",
        "aliases": [
            "text embeddings", "vector embeddings", "embeddings",
        ],
    },
    "semantic_search": {
        "display_name": "Semantic Search",
        "category": "concepts",
        "aliases": ["semantic search"],
    },
    "hybrid_search": {
        "display_name": "Hybrid Search",
        "category": "concepts",
        "aliases": ["hybrid search"],
    },
    "reranking": {
        "display_name": "Retrieval Reranking",
        "category": "concepts",
        "aliases": [
            "retrieval reranking", "retrieval re-ranking",
            "reranking", "re-ranking",
        ],
    },
    "agentic_ai": {
        "display_name": "Agentic AI",
        "category": "concepts",
        "aliases": [
            "agentic artificial intelligence", "agentic ai",
        ],
    },
    "multi_step_agents": {
        "display_name": "Multi-step Agents",
        "category": "concepts",
        "aliases": [
            "multi-step agents", "multi step agents",
            "multi-step agent",
        ],
    },
    "tool_calling": {
        "display_name": "Tool Calling",
        "category": "concepts",
        "aliases": ["tool calling", "tool calls"],
    },
    "workflow_orchestration": {
        "display_name": "Workflow Orchestration",
        "category": "concepts",
        "aliases": ["workflow orchestration", "orchestration"],
    },
    "human_in_the_loop": {
        "display_name": "Human-in-the-loop",
        "category": "concepts",
        "aliases": [
            "human-in-the-loop", "human in the loop",
            "human approval", "human approval workflows",
        ],
    },
    "llm_evaluation": {
        "display_name": "LLM Evaluation",
        "category": "concepts",
        "aliases": [
            "large language model evaluation",
            "llm evaluation", "llm evaluations",
        ],
    },
    "retrieval_accuracy": {
        "display_name": "Retrieval Accuracy",
        "category": "concepts",
        "aliases": ["retrieval accuracy"],
    },
    "hallucination_detection": {
        "display_name": "Hallucination Detection",
        "category": "concepts",
        "aliases": [
            "hallucination detection", "hallucination evaluation",
        ],
    },
    "groundedness": {
        "display_name": "Groundedness",
        "category": "concepts",
        "aliases": ["groundedness", "grounded responses"],
    },
    "observability": {
        "display_name": "Observability",
        "category": "concepts",
        "aliases": ["observability"],
    },
    "prompt_injection": {
        "display_name": "Prompt Injection",
        "category": "concepts",
        "aliases": ["prompt injection", "prompt-injection"],
    },
    "responsible_ai": {
        "display_name": "Responsible AI",
        "category": "concepts",
        "aliases": [
            "responsible ai",
            "responsible artificial intelligence",
        ],
    },
    "multimodal_ai": {
        "display_name": "Multimodal AI",
        "category": "concepts",
        "aliases": [
            "multimodal ai",
            "multimodal artificial intelligence",
        ],
    },
    "ocr": {
        "display_name": "Optical Character Recognition",
        "category": "concepts",
        "aliases": ["optical character recognition", "ocr"],
    },
    "latency_optimization": {
        "display_name": "Latency Optimization",
        "category": "concepts",
        "aliases": [
            "latency optimization", "latency reduction",
            "response latency",
        ],
    },
    "token_optimization": {
        "display_name": "Token Optimization",
        "category": "concepts",
        "aliases": [
            "token optimization", "token consumption",
            "token usage", "token consumption optimization",
        ],
    },
    "data_pipeline": {
        "display_name": "Data Pipelines",
        "category": "concepts",
        "aliases": [
            "data pipeline", "data pipelines",
            "processing pipeline", "processing pipelines",
        ],
    },
    "indexing": {
        "display_name": "Indexing",
        "category": "concepts",
        "aliases": [
            "indexing", "vector indexing",
            "document indexing",
        ],
    },
    "vector_database": {
        "display_name": "Vector Databases",
        "category": "concepts",
        "aliases": [
            "vector database", "vector databases",
        ],
    },
    "error_handling": {
        "display_name": "Error Handling",
        "category": "concepts",
        "aliases": [
            "error handling", "error-handling",
            "failure handling", "failure-handling",
        ],
    },
    "authentication": {
        "display_name": "Authentication",
        "category": "concepts",
        "aliases": ["authentication", "authenticating"],
    },
    "authorization": {
        "display_name": "Authorization",
        "category": "concepts",
        "aliases": ["authorization", "authorisation"],
    },
    "input_validation": {
        "display_name": "Input Validation",
        "category": "concepts",
        "aliases": ["input validation", "input-validation"],
    },
    "access_control": {
        "display_name": "Access Control",
        "category": "concepts",
        "aliases": ["access control", "access-control"],
    },
    "logging": {
        "display_name": "Logging",
        "category": "concepts",
        "aliases": ["logging", "application logging"],
    },
    "tracing": {
        "display_name": "Tracing",
        "category": "concepts",
        "aliases": [
            "tracing", "distributed tracing",
            "request tracing",
        ],
    },
    "monitoring": {
        "display_name": "Monitoring",
        "category": "concepts",
        "aliases": ["monitoring", "application monitoring"],
    },
    "fine_tuning": {
        "display_name": "Fine-tuning",
        "category": "concepts",
        "aliases": [
            "fine-tuning", "fine tuning",
            "model fine-tuning", "model fine tuning",
        ],
    },
    "security": {
        "display_name": "Application Security",
        "category": "concepts",
        "aliases": [
            "application security", "api security",
            "security controls",
        ],
    },

    # ---------------------------------------------------------
    # TECHNOLOGIES
    # ---------------------------------------------------------

    "python": {
        "display_name": "Python",
        "category": "technologies",
        "aliases": [
            "python programming", "python language", "python",
        ],
    },
    "fastapi": {
        "display_name": "FastAPI",
        "category": "technologies",
        "aliases": ["fastapi", "fast api"],
    },
    "flask": {
        "display_name": "Flask",
        "category": "technologies",
        "aliases": ["flask"],
    },
    "rest_api": {
        "display_name": "REST APIs",
        "category": "technologies",
        "aliases": [
            "restful apis", "restful api",
            "rest apis", "rest api",
        ],
    },
    "api": {
        "display_name": "Application Programming Interfaces",
        "category": "technologies",
        "aliases": [
            "application programming interfaces",
            "application programming interface",
            "apis", "api",
        ],
    },
    "sql": {
        "display_name": "SQL",
        "category": "technologies",
        "aliases": ["sql"],
    },
    "json": {
        "display_name": "JSON",
        "category": "technologies",
        "aliases": ["json"],
    },
    "database": {
        "display_name": "Databases",
        "category": "technologies",
        "aliases": ["databases", "database"],
    },
    "relational_database": {
        "display_name": "Relational Databases",
        "category": "technologies",
        "aliases": [
            "relational databases", "relational database",
        ],
    },
    "git": {
        "display_name": "Git",
        "category": "technologies",
        "aliases": ["git version control", "git"],
    },
    "langchain": {
        "display_name": "LangChain",
        "category": "technologies",
        "aliases": ["langchain"],
    },
    "langgraph": {
        "display_name": "LangGraph",
        "category": "technologies",
        "aliases": ["langgraph"],
    },
    "llamaindex": {
        "display_name": "LlamaIndex",
        "category": "technologies",
        "aliases": ["llamaindex", "llama index"],
    },
    "crewai": {
        "display_name": "CrewAI",
        "category": "technologies",
        "aliases": ["crewai", "crew ai"],
    },
    "openai_agents_sdk": {
        "display_name": "OpenAI Agents SDK",
        "category": "technologies",
        "aliases": ["openai agents sdk", "openai agents"],
    },
    "faiss": {
        "display_name": "FAISS",
        "category": "technologies",
        "aliases": ["faiss"],
    },
    "chroma": {
        "display_name": "Chroma",
        "category": "technologies",
        "aliases": ["chroma", "chromadb"],
    },
    "pinecone": {
        "display_name": "Pinecone",
        "category": "technologies",
        "aliases": ["pinecone"],
    },
    "qdrant": {
        "display_name": "Qdrant",
        "category": "technologies",
        "aliases": ["qdrant"],
    },
    "pgvector": {
        "display_name": "pgvector",
        "category": "technologies",
        "aliases": ["pgvector"],
    },
    "pytorch": {
        "display_name": "PyTorch",
        "category": "technologies",
        "aliases": ["pytorch", "py torch"],
    },
    "tensorflow": {
        "display_name": "TensorFlow",
        "category": "technologies",
        "aliases": ["tensorflow"],
    },
    "huggingface_transformers": {
        "display_name": "Hugging Face Transformers",
        "category": "technologies",
        "aliases": [
            "hugging face transformers",
            "huggingface transformers",
            "transformers library",
        ],
    },
    "docker": {
        "display_name": "Docker",
        "category": "technologies",
        "aliases": ["docker"],
    },
    "kubernetes": {
        "display_name": "Kubernetes",
        "category": "technologies",
        "aliases": ["kubernetes", "k8s"],
    },
    "ci_cd": {
        "display_name": "CI/CD",
        "category": "technologies",
        "aliases": [
            "continuous integration and continuous deployment",
            "continuous integration/continuous deployment",
            "continuous integration and continuous delivery",
            "ci/cd", "ci cd",
        ],
    },
    "langsmith": {
        "display_name": "LangSmith",
        "category": "technologies",
        "aliases": ["langsmith"],
    },
    "langfuse": {
        "display_name": "Langfuse",
        "category": "technologies",
        "aliases": ["langfuse"],
    },
    "ragas": {
        "display_name": "RAGAS",
        "category": "technologies",
        "aliases": ["ragas"],
    },
    "transformers": {
        "display_name": "Transformers",
        "category": "technologies",
        "aliases": ["transformers"],
    },
    "llama": {
        "display_name": "Llama",
        "category": "technologies",
        "aliases": ["llama"],
    },
    "mistral": {
        "display_name": "Mistral",
        "category": "technologies",
        "aliases": ["mistral"],
    },
    "qwen": {
        "display_name": "Qwen",
        "category": "technologies",
        "aliases": ["qwen"],
    },
    "lora": {
        "display_name": "LoRA",
        "category": "technologies",
        "aliases": ["lora"],
    },
    "qlora": {
        "display_name": "QLoRA",
        "category": "technologies",
        "aliases": ["qlora"],
    },
    "peft": {
        "display_name": "PEFT",
        "category": "technologies",
        "aliases": ["peft"],
    },

    # ---------------------------------------------------------
    # PLATFORMS
    # ---------------------------------------------------------

    "openai": {
        "display_name": "OpenAI",
        "category": "platforms",
        "aliases": ["openai"],
    },
    "azure_openai": {
        "display_name": "Azure OpenAI",
        "category": "platforms",
        "aliases": ["azure openai", "azure-openai"],
    },
    "anthropic": {
        "display_name": "Anthropic",
        "category": "platforms",
        "aliases": ["anthropic"],
    },
    "google_gemini": {
        "display_name": "Google Gemini",
        "category": "platforms",
        "aliases": ["google gemini", "gemini"],
    },
    "aws": {
        "display_name": "Amazon Web Services",
        "category": "platforms",
        "aliases": ["amazon web services", "aws"],
    },
    "azure": {
        "display_name": "Microsoft Azure",
        "category": "platforms",
        "aliases": ["microsoft azure", "azure cloud", "azure"],
    },
    "gcp": {
        "display_name": "Google Cloud Platform",
        "category": "platforms",
        "aliases": ["google cloud platform", "google cloud", "gcp"],
    },

    # ---------------------------------------------------------
    # STANDARDS AND PROTOCOLS
    # ---------------------------------------------------------

    "mcp": {
        "display_name": "Model Context Protocol",
        "category": "standards",
        "aliases": ["model context protocol", "mcp"],
    },
}
