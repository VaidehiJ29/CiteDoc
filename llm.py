import os
import time
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

class LLMError(Exception):
    """Raised when a model call fails in a way the app should show to the user."""


def _generate_gemini(prompt: str) -> str:
    from google import genai

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is missing from your .env file.")

    client = genai.Client(api_key=key)
    for attempt in range(3):
        try:
            reply = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return reply.text
        except Exception as e:
            # 429 = free-tier limit hit: wait a bit (5s, 10s, 20s) and try again
            if "429" in str(e) and attempt < 2:
                time.sleep(5 * 2 ** attempt)
                continue
            raise LLMError(f"Gemini call failed: {e}") from e


def _generate_ollama(prompt: str) -> str:
    try:
        import ollama

        client = ollama.Client(timeout=900)  # wait up to 15 minutes
        reply = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0, "num_ctx": 4096},
        )
        return reply["message"]["content"]
    except Exception as e:
        raise LLMError(
            f"Ollama call failed. Is the Ollama app running and the model downloaded? {e}"
        ) from e


def generate(prompt: str, provider: str = "gemini") -> str:
    if provider == "gemini":
        return _generate_gemini(prompt)
    if provider == "ollama":
        return _generate_ollama(prompt)
    raise LLMError(f"Unknown provider: {provider}")