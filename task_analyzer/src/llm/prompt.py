from pathlib import Path

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "task_analyzer-v1.md"

def load_system_prompt() -> str:
    return PROMPT_PATH.read_text().strip()