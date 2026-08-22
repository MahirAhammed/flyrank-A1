import time
import random
import logging
import json
from openai import OpenAI, RateLimitError, APIStatusError, APITimeoutError, AuthenticationError

from task_analyzer.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger("task_analyzer.llm")

client = OpenAI(base_url= LLM_BASE_URL, api_key= LLM_API_KEY, timeout= 30.0, max_retries= 0)

def _retry_delay(exc, attempt: int) -> float:
    """Exponential backoff plus jitter, and obeys Retry-After if present."""
    response = getattr(exc, "response", None)
    retry_after = response.headers.get("retry-after") if response is not None else None
    if retry_after:
        return float(retry_after)
    return (2**attempt) + random.uniform(0, 1)


def _call_with_retry(fetcth_fn, *args, max_attempts = 3, **kwargs):
    """Implement retry logic on 429 and 5xx and return on 400/401/403"""
    for attempt in range(max_attempts):
        try:
            return fetcth_fn(*args, **kwargs)
        
        except RateLimitError as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(_retry_delay(e, attempt))

        except APIStatusError as e:
            if e.status_code < 500:
                raise
            if attempt == max_attempts - 1:
                raise
            time.sleep(_retry_delay(e, attempt))

        except APITimeoutError as exc:
            if attempt == max_attempts - 1:
                raise
            time.sleep(_retry_delay(exc, attempt))


def _log_call(prompt_version: str, input_tokens: int, output_tokens: int, duration_ms: int, needed_repair: bool):
    logger.info(json.dumps({
        "prompt_version": prompt_version,
        "model": LLM_MODEL,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "needed_repair": needed_repair,
    }))


def call_llm(system_prompt: str, user_prompt: str, prompt_version: str):
    start = time.monotonic()
    res = _call_with_retry(
        client.chat.completions.create,
        model= LLM_MODEL,
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature= 0.2,
    )
    duration = int((time.monotonic() - start) * 1000)
    _log_call(prompt_version, res.usage.prompt_tokens, res.usage.completion_tokens, duration, needed_repair= False)
    return res.choices[0].message.content


def recall_llm(system_prompt: str, user_prompt: str, prompt_version: str, invalid_output: str, error: str) -> str:
    start = time.monotonic()
    res = _call_with_retry(
        client.chat.completions.create,
        model= LLM_MODEL,
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": invalid_output},
            {
                "role": "user",
                "content": (
                    f"Your previous answer was rejected for this reason: {error}\n"
                    "Return only corrected JSON matching the schema. "
                    "No markdown fences and no additional comments, just the JSON object alone."
                ),
            }
        ],
        temperature= 0.2,
    )
    duration = int((time.monotonic() - start) * 1000)
    _log_call(prompt_version, res.usage.prompt_tokens, res.usage.completion_tokens, duration, needed_repair= True)
    return res.choices[0].message.content