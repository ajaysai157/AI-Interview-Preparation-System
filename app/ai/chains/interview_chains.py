import logging
from typing import Any

from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from app.ai.exceptions import LLMError
from app.ai.llm import get_llm
from app.ai.prompts import EVALUATION_PROMPT, QUESTION_GENERATION_PROMPT, REPORT_PROMPT
from app.schemas.evaluation import EvaluationBase
from app.schemas.question import QuestionBase
from app.schemas.result import FinalResultResponse

logger = logging.getLogger(__name__)


def safe_invoke(chain: Any, inputs: dict, operation: str) -> Any:
    """Invokes a LangChain runnable and converts provider-level failures into LLMError."""
    try:
        return chain.invoke(inputs)
    except LLMError:
        raise
    except OutputParserException as exc:
        logger.exception("LLM returned malformed output while %s.", operation)
        raise LLMError(
            f"AI service returned output that could not be parsed while {operation}.",
            status_code=502,
        ) from exc
    except ValidationError as exc:
        logger.exception("LLM returned output that failed validation while %s.", operation)
        raise LLMError(
            f"AI service returned output that failed validation while {operation}.",
            status_code=502,
        ) from exc
    except TimeoutError as exc:
        logger.exception("LLM request timed out while %s.", operation)
        raise LLMError(f"AI service timed out while {operation}.") from exc
    except Exception as exc:
        logger.exception("LLM request failed while %s.", operation)
        raise LLMError(f"AI service encountered an error while {operation}.") from exc


def get_question_generation_chain():
    """Returns the LangChain LCEL chain for generating a new interview question.

    Uses temperature 0.7 for varied, role-tailored questions.
    """
    llm = get_llm(temperature=0.7)
    structured_llm = llm.with_structured_output(QuestionBase)
    return QUESTION_GENERATION_PROMPT | structured_llm


def get_answer_evaluation_chain():
    """Returns the LangChain LCEL chain for evaluating a candidate's answer.

    Uses temperature 0.2 for objective, deterministic grading.
    """
    llm = get_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(EvaluationBase)
    return EVALUATION_PROMPT | structured_llm


def get_report_generation_chain():
    """Returns the LangChain LCEL chain for generating the final report summary.

    Uses temperature 0.3 for structured synthesis.
    """
    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(FinalResultResponse)
    return REPORT_PROMPT | structured_llm