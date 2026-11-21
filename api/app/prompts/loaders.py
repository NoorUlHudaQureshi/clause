from pathlib import Path

PROMPTS_DIR = Path(__file__).parent  # api/app/prompts

def get_prompt(name: str, verison: str = "v1") -> None:
    return (PROMPTS_DIR / name / f"{verison}.md").read_text(encoding="utf-8").strip()


#name : agent_name/prompt_name ?
# name : support/system


# Version : v1





# Path: api/app/prompts/support/system/v2