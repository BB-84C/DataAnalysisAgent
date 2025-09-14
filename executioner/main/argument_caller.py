import os
import json
import streamlit as st
from typing import Optional, Dict, List
from namespace_mngr.namespace_manager import get_nmManager
from openai import OpenAI

# client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

namespace_mgr = get_nmManager()

_CLIENT: Optional[OpenAI] = None
_CLIENT_KEY: Optional[str] = None
_CLIENT_GEN: int = -1   

def _read_settings():
    if st is not None:
        settings = getattr(st.session_state, "settings", None)
        if isinstance(settings, dict):
            return settings
    # Not called by streamlit but called by debug
    return {
        "openai_api_key": (os.getenv("OPENAI_API_KEY") or "").strip(),
        "api_generation": 0,
    }

def _ensure_client():
    """
    Rebuild the client only on the first call, or when a change in settings['api_generation'] is detected.
    Otherwise, reuse the same client throughout to avoid unnecessary resets.
    """
    global _CLIENT, _CLIENT_KEY, _CLIENT_GEN
    settings = _read_settings()
    key = (settings.get("openai_api_key") or "").strip()
    gen = int(settings.get("api_generation") or 0)

    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Please fill in the Settings panel and click 'Apply API change'.")

    # Created for the first time
    if _CLIENT is None:
        _CLIENT = OpenAI(api_key=key)
        _CLIENT_KEY = key
        _CLIENT_GEN = gen
        return

    # Rebuild only if generation changes as a result of an "explicit application".
    if gen != _CLIENT_GEN:
        _CLIENT = OpenAI(api_key=key)
        _CLIENT_KEY = key
        _CLIENT_GEN = gen
        return
    # If generation remains unchanged, the existing client is maintained and no action is taken.

def get_client() -> OpenAI:
    _ensure_client()
    return _CLIENT  # type: ignore

def match_output_vars_to_MRs(
    mr_descriptions: dict[str, str],   # MR_EditorID -> natural language description
    runtime_outputs: dict[str, dict],   # var_name -> {class, size, status}
    runtime_EDID:str | None = None,
    model: str = "gpt-5-nano",
) -> List[str]:
    """
    Ask LLM to assign each output (in order) to a suitable MR_EditorID.
    Only MR_EditorIDs should appear in the result list.
    """
    message = _build_ordered_prompt(runtime_outputs, mr_descriptions)
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )
    
    # token usage -> NamespaceManager
    try:
        usage = getattr(response, "usage", None) or {}
        namespace_mgr.log_llm_tokens(
            runtime_EDID=runtime_EDID,
            source="argument_caller",
            model=model,
            prompt_tokens=getattr(usage, "prompt_tokens", None) or usage.get("prompt_tokens"),
            completion_tokens=getattr(usage, "completion_tokens", None) or usage.get("completion_tokens"),
            total_tokens=getattr(usage, "total_tokens", None) or usage.get("total_tokens"),
        )
    except Exception as _:
        # Security pocket: no impact on mainstream processes
        pass

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