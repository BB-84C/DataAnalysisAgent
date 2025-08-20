import os
import json
from namespace_mngr.namespace_manager import get_nmManager
from openai import OpenAI
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

namespace_mgr = get_nmManager()

def tool_caller(
        OP_Description:str,
        input_data:list[str],
        input_MR_Description: dict[str, str],
        tool_schema='', 
        model="gpt-5-mini"
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

    # There are tools available to allow LLM to automatically pick
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tool_schema,
        tool_choice="auto"
    )
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
