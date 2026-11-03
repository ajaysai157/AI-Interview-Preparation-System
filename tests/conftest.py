import os

# The test suite must be deterministic and offline, so we force the mock LLM
# provider for every test regardless of the developer's local .env (which may
# point at a real Ollama server or an external API).
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_MODEL"] = "mock-model"

from app.config import settings  # noqa: E402

settings.LLM_PROVIDER = "mock"
settings.LLM_MODEL = "mock-model"
