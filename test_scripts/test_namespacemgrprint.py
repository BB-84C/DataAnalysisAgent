from namespace_mngr.namespace_manager import NamespaceManager

# 1. 初始化 Namespace Manager
nm = NamespaceManager()

# 2. 调用 snapshot_workspace
snapshot = nm.snapshot_workspace()

# 3. 打印结果
print("Snapshot result:")
for var_name, info in snapshot.items():
    print(f"{var_name} -> class: {info['class']}, size: {info['size']}")

import sys
import os
from namespace_mngr.namespace_manager import NamespaceManager

nm = NamespaceManager()
eng = nm.eng

result = eng.eval("rand(3,3)", nargout = 1)

print("Returned result from MATLAB:")
print(result)