import logging
from typing import Any, Optional, Type
from pydantic import BaseModel
from langchain_core.runnables import Runnable

from app.config import settings

logger = logging.getLogger(__name__)


class MockStructuredRunnable(Runnable):
    def __init__(self, schema: Type[BaseModel]):
        self.schema = schema

    def invoke(self, input: Any, config: Any = None) -> BaseModel:
        schema_name = self.schema.__name__
        logger.info(f"[MockLLM] Invoked structured output for schema: {schema_name}")

        input_str = str(input).lower()

        # 1. Question Generation Schema
        if "Question" in schema_name:
            difficulty = "medium"
            if "target difficulty: easy" in input_str:
                difficulty = "easy"
            elif "target difficulty: hard" in input_str:
                difficulty = "hard"
            elif "target difficulty: medium" in input_str:
                difficulty = "medium"

            topic = "Python Core"
            if "interview type: hr" in input_str:
                topic = "Behavioral"
            elif "interview type: mixed" in input_str:
                topic = "Mixed Fundamentals"

            question_text = "What is the difference between a list and a tuple in Python, and when would you use each?"
            if topic == "Behavioral":
                question_text = "Tell me about a challenging situation you faced in a team project and how you resolved it."
            elif difficulty == "easy":
                question_text = "What are the primary data types in Python?"
            elif difficulty == "hard":
                question_text = "How does Python's Garbage Collection mechanism work, and what is the role of generational collection?"

            return self.schema(
                question=question_text,
                topic=topic,
                difficulty=difficulty,
            )

        # 2. Evaluation Schema
        elif "Evaluation" in schema_name:
            score = 7.5
            feedback = "The candidate provided a clear and structured technical explanation."
            improvement_areas = ["Consider discussing performance and memory overhead trade-offs in depth."]

            if "fail" in input_str or "weak" in input_str or "poor" in input_str or "bad" in input_str:
                score = 3.0
                feedback = "The answer lacked depth, omitted key concepts, or was technically inaccurate."
                improvement_areas = ["Provide concrete examples", "Explain core architectural principles", "Address edge cases"]
            elif "perfect" in input_str or "excellent" in input_str or "strong" in input_str or "outstanding" in input_str:
                score = 9.5
                feedback = "Exceptional response demonstrating deep mechanical understanding and architectural clarity."
                improvement_areas = []

            return self.schema(
                score=score,
                correctness=min(10.0, score + 0.5),
                completeness=max(0.0, score - 0.5),
                clarity=score,
                relevance=min(10.0, score + 1.0),
                feedback=feedback,
                improvement_areas=improvement_areas,
            )

        # 3. Final Report / Result Schema
        elif "Result" in schema_name:
            return self.schema(
                overall_score=85.0,
                strengths=["Demonstrated strong system architecture comprehension", "Clear and concise technical communication"],
                weaknesses=["Needs to reinforce concurrency models and async event loops"],
                topic_performance={"Python Core": 88.0, "System Architecture": 80.0, "Communication": 90.0},
                recommendations=["Explore Python GIL internals and asyncio primitives", "Practice designing high-throughput distributed systems"],
                interview_summary="The candidate exhibited solid technical competence, strong problem-solving logic, and structured communication throughout the interview session.",
            )

        try:
            return self.schema()
        except Exception:
            return None


class MockLLM:
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    def with_structured_output(self, schema: Type[BaseModel], **kwargs: Any) -> MockStructuredRunnable:
        return MockStructuredRunnable(schema)

    def invoke(self, input: Any, config: Any = None) -> Any:
        from langchain_core.messages import AIMessage
        return AIMessage(content="Structured mock response.")


def get_llm(temperature: float = 0.7):
    """Centralized LLM Factory.

    Returns the configured LLM provider instance:
    - Ollama (default local with qwen3:4b)
    - Mock (for offline development & testing)
    - Optional external API providers (OpenAI, Anthropic, Google) if API keys are set.
    """
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL

    logger.info(f"Initializing LLM provider: {provider}, model: {model}, temperature: {temperature}")

    if provider == "mock":
        return MockLLM(model, temperature=temperature)

    elif provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=model,
                temperature=temperature,
            )
        except Exception:
            # Fallback to OpenAI-compatible endpoint on local Ollama daemon
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                base_url=f"{settings.OLLAMA_BASE_URL}/v1",
                api_key="ollama",
                model=model,
                temperature=temperature,
            )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = settings.OPENAI_API_KEY
        api_model = settings.OPENAI_MODEL or "gpt-4o"
        return ChatOpenAI(model=api_model, api_key=api_key, temperature=temperature)

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = settings.ANTHROPIC_API_KEY
        api_model = settings.ANTHROPIC_MODEL or "claude-3-5-sonnet-20241022"
        return ChatAnthropic(model=api_model, api_key=api_key, temperature=temperature)

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = settings.GOOGLE_API_KEY
        api_model = settings.GOOGLE_MODEL or "gemini-1.5-pro"
        return ChatGoogleGenerativeAI(model=api_model, api_key=api_key, temperature=temperature)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
