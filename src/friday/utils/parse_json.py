import json
import re

def parse_json_from_model(output: str):
    # remove ```json ... ``` or ``` ... ``` blocks
    cleaned = re.sub(r"```json(.*?)```", r"\1", output, flags=re.DOTALL)
    cleaned = re.sub(r"```(.*?)```", r"\1", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None
