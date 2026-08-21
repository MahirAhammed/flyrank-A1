from openai import OpenAI
from task_analyzer.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

client = OpenAI(base_url= LLM_BASE_URL, api_key= LLM_API_KEY, timeout= 60.0)

def call_llm(system_prompt: str, user_prompt: str):
    res = client.chat.completions.create(
        model= LLM_MODEL,
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature= 0.2,
        timeout= 60,
    )
    return res.choices[0].message.content


def recall_llm(system_prompt: str, user_prompt: str, invalid_output: str, error: str) -> str:
    res = client.chat.completions.create(
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
        timeout= 60
    )
    return res.choices[0].message.content