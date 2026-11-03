import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.exceptions import LLMError
from app.api.interviews import router as interview_router
from app.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Interview Preparation & Evaluation System",
    description=(
        "AI-powered mock interview platform. Create a configurable interview, "
        "answer LLM-generated questions, receive structured evaluations with adaptive "
        "difficulty, and finish with a full performance report. The workflow is an "
        "orchestrated LangGraph state machine with human-in-the-loop review support. "
        "Consumed by the React frontend (frontend/) as well as any REST client."
    ),
    version="0.1.0",
)

# Allow the web frontend (Vite dev server / static build) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(interview_router)


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Interview System",
    }