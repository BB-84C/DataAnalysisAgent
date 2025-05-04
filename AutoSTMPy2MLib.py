import numpy as np 
import matplotlib.pyplot as plt
import matlab.engine
import os
import io
import inspect

m=matlab.engine.start_matlab("-desktop")

def py_opensxm(pnum):
    """_summary_

    Args:
        punm (string): pnum, it's either 1 or 2. 1 means only open topo, 2 means open all channels.
    """
    m.opensxm(int(pnum),nargout=0)
    cfig = m.gcf()
    
    