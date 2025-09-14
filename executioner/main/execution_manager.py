# executioner/main/execution_manager.py

import json
import importlib.util
import os
import types
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from namespace_mngr.namespace_manager import get_nmManager
from executioner.main.tool_caller import tool_caller
from executioner.main.argument_caller import match_output_vars_to_MRs

class ExecutionManager:
    def __init__(self, data_path: str, flow_path: str, tool_list_path = str, tool_schema_path = str):
        """
        Central execution management system for TaskGraph.
        Loads node/runtime definitions (data) and runtime execution order (flow).
        """
        self.tool_list_path = tool_list_path
        self.tool_schema_path = tool_schema_path
        self.tool_list = []
        self.tool_schema = {}
        
        # Load data and flow JSON
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        with open(flow_path, 'r') as f:
            self.flow = json.load(f)
        # Extract runtimes and node info
        self.nodes = self.data.get("nodes", [])
        self.runtimes = self.data.get("runtimes", [])
        self.flows = self.flow.get("flows",[])
        self.node_map = {n["EditorID"]: n for n in self.nodes}  # EditorID -> node object
        self.runtimes_by_editor_id = {r["EditorID"]: r for r in self.runtimes}
        self.entry_runtimes = self.flows[0].get("entry_runtimes", [])
        # Assuming only one flow per flow.json for now
        
        # Initialize for parallel processing and task pool
        self.ThPExecutor = ThreadPoolExecutor(max_workers=4)
        self.futures = {}   # MR_ID or Param_ID -> Future     
        self.op_submit_map = {}  # OP EditorID -> Future (runtime)

        # Initialize Namespace Manager
        self.namespace_mgr = get_nmManager()
        
    def Registration(self):
        # Register MR and Param nodes as futures
        for node in self.nodes:
            edid = node["EditorID"]
            if edid.startswith("MR_") or edid.startswith("Param_"):
                f = Future()
                self.futures[edid] = f
                if edid.startswith("Param_"):
                    f.set_result(node["description"])
        
        # Register OP runtimes             
        for rt in self.runtimes:
            edid = rt["EditorID"]
            current_node = rt["current_node"]
            if current_node.startswith("OP_"):
                self.op_submit_map[edid] = self.ThPExecutor.submit(self._run_op_runtime, edid)
        
        print(f"[Init] Done registration for nodes and runtimes.")


    
    def _run_op_runtime(self, runtime_edid:str):
        rt = self.runtimes_by_editor_id[runtime_edid]
        current_node = rt["current_node"]
        entry_edges = rt.get("entry_edge",[])
        input_data = []
        input_MR_Description = {}
        available_tools = {tool.__name__: tool for tool in self.tool_list}
        OP_description = self.node_map[current_node]["description"]
        for edge in sorted(entry_edges, key=lambda e: e.get("order", 0)):
            from_id = edge["from"]
            val = self.futures[from_id].result() # blockage waiting
            input_data.append(val)
            description = self.node_map[from_id]["description"]
            input_MR_Description[from_id] = description
        
        self.namespace_mgr.start_runtime(runtime_edid)
        
        # Tool call and execution    
        tool_calls_response = tool_caller(OP_description,input_data, input_MR_Description, self.tool_schema,runtime_edid)
        print(f"[Execution] Done tool call:{tool_calls_response}")
        if tool_calls_response:
            for tool_call in tool_calls_response:
                    # Get function name
                    function_name = tool_call.function.name
                    # Get the function object
                    function_to_call = available_tools[function_name]
                    # Get the function parameters
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except Exception:
                        function_args = {}
                    # Input the function parameters into the function to get the result of the function calculation
                    function_to_call(**function_args)
        
        self.namespace_mgr.end_runtime(runtime_edid)
        # Placeholder for tool call result
        output = self.namespace_mgr.runtime_outputs[runtime_edid]
        mr_descs = {}
        for edge in rt.get("next_edge", []):
            to_id = edge["to"]
            description = self.node_map[to_id]["description"]
            mr_descs[to_id] = description
            
        output_keys = [
            var_name
            for var_name, meta in output.items()
            if not (isinstance(meta, dict) and meta.get("status") == "deleted")
        ]
        mr_keys = list(mr_descs.keys())
        print(f"[Execution] Output_keys = {output_keys}, MR_keys = {mr_keys}")
        if len(output_keys) == 1 and len(mr_keys) == 1:
            output_var = output_keys[0]
            mr_edid = mr_keys[0]
            if mr_edid not in self.futures:
                self.futures[mr_edid] = Future()
                print(f"[Exception!] MR node: {mr_edid} generated by runtime: {runtime_edid} is not registered at initialzation")
            self.futures[mr_edid].set_result(output_var)
        else:
            if len(output_keys) != len(mr_keys):
                print(f"[Exception] Output count != MR count in {runtime_edid}. LLM fallback invoked.")  
            result = match_output_vars_to_MRs(mr_descs, output,runtime_edid)  # LLM returns MR list 
            for i, mr_edid in enumerate(result):
                output_var = output_keys[i]
                if mr_edid not in self.futures:
                    self.futures[mr_edid] = Future()
                    print(f"[Exception!] MR node: {mr_edid} generated by runtime: {runtime_edid} is not registered at initialzation")
                self.futures[mr_edid].set_result(output_var)
        print(f"[NamespaceManager] Runtime token Usage: {self.namespace_mgr.get_runtime_token_summary(runtime_edid)}")
        print(f"[NamespaceManager] Cumulative total token Usage: {self.namespace_mgr.get_total_token_summary()}")
        
                
        

        
    
    def trigger_entry_runtime(self, runtime_edid:str):
        rt = self.runtimes_by_editor_id[runtime_edid]
        current_node = rt["current_node"]
        desc = self.node_map[current_node]["description"]
        self.futures[current_node].set_result(desc)
        print(f"[Init] Set entry MR {current_node} = {desc}")
        
    def run(self):
        self._load_tools()
        self.Registration()
        self.trigger_entry_runtime(self.entry_runtimes[0])
    
    def _load_tools(self):
        module_name  = os.path.splitext(os.path.basename(self.tool_list_path))[0]
        spec = importlib.util.spec_from_file_location(module_name,self.tool_list_path)
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)
        
        for name in dir(tool_module):
            if name.startswith("_"):
                continue
            attr = getattr(tool_module, name)
            if (
                isinstance(attr, types.FunctionType) and
                attr.__module__ == module_name  # Only include functions defined in this file
            ):
                self.tool_list.append(attr)
        
        with open(self.tool_schema_path, "r") as f:
            self.tool_schema = json.load(f)




