from pathlib import Path

PROMPT_DIR = Path(__file__).parent.parent.parent / "prompts"
DEFAULT_FILE = "task_analyzer-v1.md"

def load_system_prompt(prompt_file: str = DEFAULT_FILE) -> tuple[str, str]:
    path = PROMPT_DIR / prompt_file
    prompt = path.read_text().strip()
    version = path.stem.rsplit("-", 1)[-1]
    return prompt, version