"""Utility to inject a workflow into the Flow Editor and trigger execution."""

import os
import re
import sys
from pathlib import Path

MERMAID_WORKFLOW = """flowchart TD
    MR_1[("file names = '07_15_25_002.sxm'" )] -- in_1 --> OP_1["opensxm"]
    Param_1("pnum = 1") -- in_2 --> OP_1
    OP_1 -- out --> MR_2[("fig_07_15_25_002, 1x1 Figure")]
    MR_2 -- in_2 --> OP_2["background subtraction along row"]
    Param_2("pnum = 2") -- in_2 --> OP_2
    OP_2 -- out --> MR_3[("fig_07_15_25_002_polyback2, 1x1 Figure")]
    MR_3 -- in_1 --> OP_3["fourier transform"]
    Param_3("pnum = 3") -- in_2 --> OP_3
    OP_3 -- out --> MR_4[("fig_07_15_25_002_FT, 1x1 Figure")]
    MR_4 -- in_1 --> OP_4["extract linecut"]
    Param_4("lincut param = [1,1,-1,176,246,176,211]") -- in_2 --> OP_4
    OP_4 -- out --> MR_5[("fig_07_15_25_002_Linecut, 1x1 Figure")]"""


def _update_flow_editor_text(flow_html: Path, mermaid_text: str) -> None:
    """Replace the default textarea content in the flow editor HTML."""
    html = flow_html.read_text(encoding="utf-8")
    pattern = r'(<textarea[^>]*id="mermaid-input"[^>]*>)([\\s\\S]*?)(</textarea>)'
    replacement = r"\\1\\n" + mermaid_text + r"\\n\\3"
    new_html = re.sub(pattern, replacement, html, flags=re.MULTILINE)
    flow_html.write_text(new_html, encoding="utf-8")


def _run_flow():
    """Invoke the same execution routine as the Flow UI Run button."""
    root_path = r"/Users/bb84/Documents/Research/DataAnalysisAgent"
    tool_py = r"/external_tools/STM_Lab/stm_lab_scripts_lib.py"
    tool_schema = r"/external_tools/STM_Lab/stm_lab_script_lib_schema.json"

    data_path = os.path.normpath(root_path + "/workflow_lib/simpletest - data.json")
    flow_path = os.path.normpath(root_path + "/workflow_lib/simpletest - flow.json")

    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from executioner.main import execution_manager

    executor = execution_manager.ExecutionManager(
        data_path,
        flow_path,
        os.path.normpath(root_path + tool_py),
        os.path.normpath(root_path + tool_schema),
    )
    executor.run()


def insert_workflow_and_execute() -> None:
    """Update flow editor default text and simulate clicking Run."""
    flow_html = Path(__file__).resolve().parent / "ui_interface" / "panels" / "flow_control" / "flow_split.html"
    _update_flow_editor_text(flow_html, MERMAID_WORKFLOW)
    # _run_flow()


if __name__ == "__main__":
    insert_workflow_and_execute()
