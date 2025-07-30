# namespace_mngr/namespace_manager.py

import matlab.engine
import numpy as np

def notify_matlab_execution(script_name, params):
    """
    Record that a MATLAB execution occurred.
    Optionally trigger workspace diff check (if enabled).
    """
    print(f"[Namespace Manager] MATLAB script executed: {script_name} with params {params}")
    # TODO: trigger workspace sync or mark dirty state

def check_workspace_diff():
    """
    Compare MATLAB workspace state and return new/updated variables.
    """
    names = matlab.engine.find_matlab()
    if not names:
        return {}

    eng = matlab.engine.connect_matlab(names[0])

    # Fetch variable list
    var_list = set(eng.eval("who", nargout=1))
    # Compare with stored previous state (implement state storage here)
    # Return diff for UI update
