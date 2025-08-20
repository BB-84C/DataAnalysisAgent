import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from executioner.main.argument_caller import match_output_vars_to_MRs

mr_decs = {
    "MR_2": "topographic image",
    "MR_3": "fft of topo"
  }
output= {
    "fft":  {"class": "double", "size": "256x256", "status": "added"},
    "topo": {"class": "double", "size": "256x256", "status": "added"}
}

result = match_output_vars_to_MRs(mr_decs,output)
output_keys = list(output.keys())

for i, mr_edid in enumerate(result):
    output_var = output_keys[i]
    output_val = output[output_var]
print(result)