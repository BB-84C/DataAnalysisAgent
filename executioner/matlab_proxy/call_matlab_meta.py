import json
import matlab.engine
import numpy as np
from namespace_mngr.namespace_manager import notify_matlab_execution

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
    # 1. Connect to MATLAB engine
    names = matlab.engine.find_matlab()
    if not names:
        raise RuntimeError("No MATLAB session found. Run 'matlab.engine.shareEngine' in MATLAB.")
    eng = matlab.engine.connect_matlab(names[0])

    # 2. Prepare parameters for MATLAB call
    script_name = meta["script"]
    params = meta.get("params", {})
    # vars_before = set(eng.eval("who", nargout=1))

    # Convert params to MATLAB workspace variables
    args = []
    for key, val in params.items():
        if isinstance(val, str):
            # Pass string as MATLAB char array
            args.append(f"'{val}'")
        else:
            # Pass numeric directly
            args.append(str(val))
    args_str = ", ".join(args)

    # Execute MATLAB script with arguments
    if args_str:
        eng.eval(f"{script_name}({args_str});", nargout=0)
    else:
        eng.eval(f"{script_name}();", nargout=0)

    # # 4. Fetch outputs from MATLAB workspace
    # vars_after = set(eng.eval("who",nargout=1))
    # new_vars = vars_after - vars_before
    # result = {}
    # for var_name in new_vars:
    #     try:
    #         matlab_var = eng.eval(f"evalin('base', '{var_name}')", nargout=1)
    #         # Convert MATLAB variable to Python
    #         if isinstance(matlab_var, matlab.double):
    #             result[var_name] = np.array(matlab_var)
    #         elif isinstance(matlab_var, (str, float, int)):
    #             result[var_name] = matlab_var
    #         else:
    #             result[var_name] = str(matlab_var)  # Fallback to string representation
    #     except Exception as e:
    #         result[var_name] = None
    #         print(f"Warning: Failed to fetch variable {var_name}: {e}")
    # return(result)

    notify_matlab_execution(script_name,params)
    return {"status": "executed", "script": script_name}
