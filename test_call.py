import sys
import os

from executioner import call_matlab_meta

path = "F:/Dropbox/STM_data/Unisoku/2025-07-13"
fn = "07_15_25_002.sxm"
pnum = 1
call_matlab_meta({
        "script": "opensxm_auto",
        "params": {
            "path": path,
            "fn": fn,          
            "pnum": pnum
        },
        "outputs": ["sxm_data"]
    })


