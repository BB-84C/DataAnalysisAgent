import os
import json
from typing import List,Dict
from openai import OpenAI
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def match_output_vars_to_MRs(
    mr_descriptions: dict[str, str],   # MR_EditorID -> natural language description
    runtime_outputs: dict[str, dict],   # var_name -> {class, size, status}
    model: str = "gpt-5-nano"
) -> List[str]:
    """
    Ask LLM to assign each output (in order) to a suitable MR_EditorID.
    Only MR_EditorIDs should appear in the result list.
    """
    message = _build_ordered_prompt(runtime_outputs, mr_descriptions)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )

    # Parse LLM JSON reply
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[argument_call] Failed to parse LLM response: {e}")
        return []


def _build_ordered_prompt(outputs: List[str], mr_descriptions: Dict[str, str]) -> str:
    return (
        "You are given a list of output variables from a runtime, and a set of result slots (MR nodes) "
        "to assign them to. Each MR has a natural language description.\n\n"
        "Your task is: for each output variable, in order, choose the most suitable MR_EditorID from the list below. "
        "Only use the MR keys provided. Do NOT invent variable names or MR names.\n\n"
        f"Outputs (in order):\n{json.dumps(outputs, indent=2)}\n\n"
        f"MR candidates:\n{json.dumps(mr_descriptions, indent=2)}\n\n"
        "Return ONLY a JSON list of MR_EditorIDs, like:\n[\"MR_2\", \"MR_3\"]"
    )