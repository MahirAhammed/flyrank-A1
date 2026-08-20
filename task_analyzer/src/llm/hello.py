from openai import OpenAI
from task_analyzer.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)

res = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
)

print(res.choices[0].message.content)