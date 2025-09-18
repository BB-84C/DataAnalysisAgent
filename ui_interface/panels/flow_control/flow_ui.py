# ui_interface/panels/flow_control/flow_ui.py

import streamlit as st
import sys
import os
import streamlit.components.v1 as components
from pathlib import Path

def render_flow_ui():
    st.subheader("Flow Control")
    st.markdown(
        """
        **Usage**

        - Write your data process/analysis workflow in Mermaid.js-style in the Flow Editor; the right side shows a live preview.
        - Each node represents a TaskGraph node (**MR** / **Param** / **OP**). It is recommended to annotate **EditorID** / description within nodes.
        - Use `-->` to indicate dependency direction; entry points start from `entry_runtimes` in `flow.json`.
        - Click **Run** to execute using `data.json` and `flow.json` specified in current settings.
        - Tool invocations and namespace logs during runtime are displayed in the right-hand **Namespace Manager Panel**.
        """
    )


    # Load HTML file path
    html_path = os.path.join(os.path.dirname(__file__), "flow_split.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Render the flow editor layout
    components.html(html_content, height=600, scrolling=False)
    
    # --- Run Button ---
    st.divider()
    if st.button("Run", type="primary"):
        settings = st.session_state.get("settings", {}) or {}
        root_path = settings.get("root_path", r"D:/GPTAutoSTM")
        tool_py = settings.get("tool_py", r"/external_tools/STM_Lab/stm_lab_scripts_lib.py")
        tool_schema = settings.get("tool_schema", r"/external_tools/STM_Lab/stm_lab_script_lib_schema.json")

        data_path = root_path+"/workflow_lib/simpletest - data.json"
        flow_path = root_path+"/workflow_lib/simpletest - flow.json"
        
        project_root = Path(__file__).resolve().parents[2]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from executioner.main import execution_manager

        executor = execution_manager.ExecutionManager(
            os.path.normpath(data_path),
            os.path.normpath(flow_path),
            os.path.normpath(root_path+tool_py),
            os.path.normpath(root_path+tool_schema)
        )
        executor.run()
        st.success("Execution Running.")
