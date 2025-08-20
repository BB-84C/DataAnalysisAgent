import json
import matlab.engine
import numpy as np
from namespace_mngr.namespace_manager import get_nmManager

nm = get_nmManager()

def call_matlab_meta(meta):
    """
    Call MATLAB script based on meta information and return specified outputs.

    Meta structure:
    {
        "script": "script_name",       # MATLAB function/script name
        "params": [...],               # dict of parameters
        "outputs": ["var1", "var2"]    # list of variable names to fetch from MATLAB workspace
    }
    """
    eng = nm.eng
    
    # 2. Prepare parameters for MATLAB call
    script_name = meta["script"]
    params = meta.get("params", {})
    # vars_before = set(eng.eval("who", nargout=1))

    # Convert params to MATLAB workspace variables
    params_raw = meta.get("params", {})
    args = []
    # Ensure uniform format: convert dict to list[dict] if needed
    if isinstance(params_raw, dict):
        params_list = [params_raw]
    elif isinstance(params_raw, list):
        params_list = params_raw
    else:
        raise ValueError(f"[call_matlab_meta] Unexpected type for 'params': {type(params_raw)}")
    
    for pair in params_list:
        for key, val in pair.items():
            if isinstance(val, str):
                # Attempts to recognize strings of pure numbers (converted to numeric)
                if val.isdigit():
                    args.append(val)  # Without quotation marks
                else:
                    args.append(f"'{val}'")  # Ordinary strings in quotes
            else:
                args.append(str(val))  # Other non-string types (e.g. int, float)
    args_str = ", ".join(args)

    # Execute MATLAB script with arguments
    if args_str:
        eng.eval(f"{script_name}({args_str});", nargout=0)
    else:
        eng.eval(f"{script_name}();", nargout=0)
    nm.log_script_call(script_name,params)
    return {"status": "executed", "script": script_name}
