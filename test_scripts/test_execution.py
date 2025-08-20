import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from executioner.main import execution_manager

executor = execution_manager.ExecutionManager("D:\GPTAutoSTM\workflow_lib\simpletest - data.json","D:\GPTAutoSTM\workflow_lib\simpletest - flow.json", "D:\GPTAutoSTM\external_tools\STM_Lab\stm_lab_scripts_lib.py","D:\GPTAutoSTM\external_tools\STM_Lab\stm_lab_script_lib_schema.json")
executor.run()