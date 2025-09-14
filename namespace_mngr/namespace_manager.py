# namespace_mngr/namespace_manager.py

import matlab.engine
import numpy as np
import threading
import time

class NamespaceManager:
    def __init__(self):
        """Initialize MATLAB engine and internal state tracking."""
        self.eng = None
        self.current_snapshot = {}
        self.runtime_snapshots = {}
        self.runtime_outputs = {}
        self.execution_log = []
        self.runtime_logs = {}
        self._connect_matlab()
        
        # Token Ledger
        self.runtime_token_usages = {}
        self.total_token_usages = []
        self._tok_lock = threading.Lock()
        
    def _connect_matlab(self):
        """Connect to existing MATLAB session."""
        names = matlab.engine.find_matlab()
        if not names:
            raise RuntimeError("No MATLAB session found. Please run 'matlab.engine.shareEngine' in MATLAB.")
        self.eng = matlab.engine.connect_matlab(names[0])

    def snapshot_workspace(self):
        """
        Take a snapshot of the current MATLAB workspace.
        Returns:
            dict: {variable_name: {"class": <str>, "size": <str>}}
        """
        snapshot = {}

        # 1. 获取所有变量名
        var_names = self.eng.eval("who", nargout=1)  # MATLAB 返回 cell array

        # 2. 遍历变量，获取 class 和 size
        for name in var_names:
            try:
                var_class = self.eng.eval(f"class({name})", nargout=1)
                var_size = self.eng.eval(f"size({name})", nargout=1)  # 返回 matlab.double
                # print(f"[NamespaceManager] var_size for {name}:", var_size, type(var_size))
                # # 将 size 转换成字符串 "MxN"
                # raw_list = var_size.tolist()
                # 存入 snapshot 字典
                size_str = "x".join(str(int(x)) for x in var_size[0])
                snapshot[name] = {"class": var_class, "size": size_str}
            except Exception as e:
                # 遇到无法获取 class/size 的变量，记录错误信息
                snapshot[name] = {"class": "Unknown", "size": "Unknown"}
                print(f"[NamespaceManager] Warning: Failed to get info for {name}: {e}")
                
        self.current_snapshot = snapshot
        print(f"[NamespaceManager] Current Workspace: {self.current_snapshot}")
        return snapshot


    def start_runtime(self, runtime_EDID):
        """Record workspace snapshot at the start of a runtime.
        
            Args:
                runtime_EDID (str): Identifier for the runtime.
        """
        start_snapshot = self.snapshot_workspace()
        self.runtime_snapshots[runtime_EDID] = {
            "start": start_snapshot,
            "end": None
        }
        if runtime_EDID not in self.runtime_token_usages:
            self.runtime_token_usages[runtime_EDID] = []
            
        print(f"[NamespaceManager] Runtime '{runtime_EDID}' started. Snapshot recorded with {len(start_snapshot)} variables.")
        

    def log_script_call(self, script_name, params, runtime_EDID=None):
        """
        Record a MATLAB script call event.

        Args:
            script_name (str): Name of the MATLAB script called.
            params (dict): Parameters passed to the script.
            runtime_EDID (str, optional): If provided, associate the call with a specific runtime.
        """
        log_entry = {"script": script_name, "params": params}

        # 全局日志
        self.execution_log.append(log_entry)

        # 如果提供了 runtime_EDID，写入该 runtime 的日志
        if runtime_EDID:
            if runtime_EDID not in self.runtime_logs:
                self.runtime_logs[runtime_EDID] = []
            self.runtime_logs[runtime_EDID].append(log_entry)

        print(f"[NamespaceManager] Recorded script call: {script_name} with params {params}")


    def end_runtime(self, runtime_EDID):
        """Compare snapshots and return newly added or modified variables.
            Args:
                runtime_EDID (str): Identifier for the runtime.

            Returns:
                dict: Newly added or modified variables with their class and size.
        """
        end_snapshot = self.snapshot_workspace()
        if runtime_EDID not in self.runtime_snapshots:
            raise ValueError(f"Runtime '{runtime_EDID}' not found. Did you call start_runtime()?")

        start_snapshot = self.runtime_snapshots[runtime_EDID]["start"]

        # 3. 计算差异
        diff = {}

        for var_name, info in end_snapshot.items():
            if var_name not in start_snapshot:
                # 新增变量
                diff[var_name] = {
                    "class": info["class"],
                    "size": info["size"],
                    "status": "added"
                    }
            else:
                # 检查是否有修改（class 或 size）
                if (info["class"] != start_snapshot[var_name]["class"] or
                    info["size"] != start_snapshot[var_name]["size"]):
                    diff[var_name] = {
                    "class": info["class"],
                    "size": info["size"],
                    "status": "modded"
                    }
        for var_name, info in start_snapshot.items():
            if var_name not in end_snapshot:
                diff[var_name] = {
                    "class": info["class"],
                    "size": info["size"],
                    "status": "deleted"
                }

        # 4. 保存结束快照和输出
        self.runtime_snapshots[runtime_EDID]["end"] = end_snapshot
        self.runtime_outputs[runtime_EDID] = diff
        
        
        print(f"[NamespaceManager] Runtime '{runtime_EDID}' ended. {len(diff)} new/modified variables detected.")
        runtime_log = self.runtime_logs.get(runtime_EDID,[])   
        return {"diff": diff, "log": runtime_log}

    def get_runtime_outputs(self, runtime_EDID):
        """
        Retrieve the outputs (diff) and log for a given runtime.

        Args:
            runtime_EDID (str): Identifier for the runtime.

        Returns:
            dict: {
                "diff": <add/modded variables>,
                "log": <scripts executed by the runtime>
            }
        """
        if runtime_EDID not in self.runtime_outputs:
            print(f"[NamespaceManager] No outputs recorded for runtime '{runtime_EDID}'.")
            return {"diff": {}, "log": self.runtime_logs.get(runtime_EDID, [])}

        return {
            "diff": self.runtime_outputs[runtime_EDID],
            "log": self.runtime_logs.get(runtime_EDID, [])
        }
        
    def get_runtime_status(self, runtime_EDID):
        """
        Infer the execution status of a runtime based on internal logs.

        Returns:
            One of: 'pending', 'running', 'success', 'failed'
        """
        if runtime_EDID not in self.runtime_snapshots:
            return "pending"
        
        if runtime_EDID in self.runtime_outputs:
            return "success"
        
        if runtime_EDID in self.runtime_logs and len(self.runtime_logs[runtime_EDID]) > 0:
            return "running"

        return "unknown"

        # --- NEW: token accounting API ---

    def log_llm_tokens(self,
                       runtime_EDID: str | None,
                       source: str,
                       model: str,
                       prompt_tokens: int | None,
                       completion_tokens: int | None,
                       total_tokens: int | None):
        """
        Append a token-usage event.
        - runtime_EDID: EDID of the current runtime; if None, it will be credited to the bottom bucket "__unknown_runtime__".
        - source: "argument_caller" / "tool_caller" / others
        - model: the name of the actual model used
        - *_tokens: null; pass None if you can't get usage (will be credited with 0)
        """
        
        if not runtime_EDID:
            runtime_EDID = "__unknown_runtime__"

        evt = {
            "source": source,
            "model": model,
            "prompt": int(prompt_tokens or 0),
            "completion": int(completion_tokens or 0),
            "total": int(total_tokens or 0),
            "ts": time.time()
        }

        with self._tok_lock:
            if runtime_EDID not in self.runtime_token_usages:
                self.runtime_token_usages[runtime_EDID] = []
            self.runtime_token_usages[runtime_EDID].append(evt)
            self.total_token_usages.append(evt)
            
    def get_runtime_token_summary(self, runtime_EDID: str) -> dict:
        """
        Return summed tokens for a given runtime.
        {
            "prompt": int, "completion": int, "total": int, "events": int
        }
        """
        with self._tok_lock:
            events = self.runtime_token_usages.get(runtime_EDID, [])
            prompt = sum(e["prompt"] for e in events)
            completion = sum(e["completion"] for e in events)
            total = sum(e["total"] for e in events)
            return {"Runtime": runtime_EDID, "prompt": prompt, "completion": completion, "total": total, "events": len(events)}

    def get_total_token_summary(self) -> dict:
        """
        Return summed tokens since last reset/begin_run (whole run/session).
        {
          "prompt": int, "completion": int, "total": int, "events": int
        }
        """
        with self._tok_lock:
            prompt = sum(e["prompt"] for e in self.total_token_usages)
            completion = sum(e["completion"] for e in self.total_token_usages)
            total = sum(e["total"] for e in self.total_token_usages)
            return {"prompt": prompt, "completion": completion, "total": total, "events": len(self.total_token_usages)}


    
    
_MGR = None
_MGR_LOCK = threading.Lock()

def get_nmManager():
    """Return the module-level singleton of NamespaceManager."""
    global _MGR
    if _MGR is None:
        with _MGR_LOCK:
            if _MGR is None:   # double-checked locking for thread-safety
                _MGR = NamespaceManager()
    return _MGR

def _reset_nmManager_for_tests():
    """(Optional) Testing helper to reset singleton between tests."""
    global _MGR
    with _MGR_LOCK:
        _MGR = None