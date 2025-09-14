import os
import json
from typing import Optional, Dict, List
from namespace_mngr.namespace_manager import get_nmManager
from openai import OpenAI
import streamlit as st

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

def tool_caller(
        OP_Description:str,
        input_data:list[str],
        input_MR_Description: dict[str, str],
        tool_schema='', 
        runtime_EDID: str | None = None,
        model="gpt-5-mini",
    )->dict:
    """
    Only responsible for:
    - Calling the LLM
    - Determining whether a tool call is triggered
    - Extract tool names and parameters
    - Returns a unified dictionary, does not execute the tool, does not write back to the namespace
    """
    messages = _build_tool_prompt(OP_Description, input_data, input_MR_Description)
    tool_called = False
    tool_name = None
    call_args = None
    client = get_client()

    # There are tools available to allow LLM to automatically pick
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tool_schema,
        tool_choice="required",
        # temperature=0.5,
        # top_p = 0,
    )
    
    # token usage -> NamespaceManager
    try:
        usage = getattr(response, "usage", None) or {}
        namespace_mgr.log_llm_tokens(
            runtime_EDID=runtime_EDID,
            source="tool_caller",
            model=model,
            prompt_tokens=getattr(usage, "prompt_tokens", None) or usage.get("prompt_tokens"),
            completion_tokens=getattr(usage, "completion_tokens", None) or usage.get("completion_tokens"),
            total_tokens=getattr(usage, "total_tokens", None) or usage.get("total_tokens"),
        )
    except Exception as _:
        pass
    
    tool_calls = response.choices[0].message.tool_calls or []
    return tool_calls


def _build_tool_prompt(OP_Description, input_data, input_MR_Description):
    
    snapshot = namespace_mgr.current_snapshot
    # Extract type info for variables
    var_type_info = {}

    for var in input_data:
        try:
            var_type_info[var] = {
                "class": snapshot[var]["class"],
                "size": snapshot[var]["size"]
            }
        except KeyError:
            # Variable not found in snapshot, likely a Param or file path, skip it
            continue
    context = (
        "You are given a set of named variables that have been prepared in the execution environment."
        "Each variable name corresponds to a known value, and you can assume all are available.\n\n"
        "Available variables:\n"
        f"{json.dumps(input_data, indent=2)}\n\n"
        "The class and size of these variables:\n"
        f"{json.dumps(var_type_info, indent=2)}\n\n"
        "Descriptions of some variables:\n"
        f"{json.dumps(input_MR_Description, indent=2)}"
    )

    task = (
        "Please select the correct tool to perform the following operation:\n"
        f"{OP_Description}\n\n"
        # "Return only the arguments required by the tool."
    )

    return [
        {"role": "system", "content": context},
        {"role": "user", "content": task}
    ]
