import sys
import os
import ast
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
# from executioner.matlab_proxy.call_matlab_meta import call_matlab_meta


# meta = {'script': 'opensxm_auto', 'params': [{'path': 'F:/Dropbox/STM_data/Unisoku/2025-07-13'}, {'filename': '07_15_25_002.sxm'}, {'pnum': '1'}], 'outputs': ['sxm_data']}
# call_matlab_meta(meta)
val = '[1,1,-1,176,246,176,211]'
parsed_val = ast.literal_eval (val)
print(type(parsed_val))
print(parsed_val[0].isdigit())
print(parsed_val)