# ui_interface/panels/flow_control/flow_ui.py

import streamlit as st
import os
import streamlit.components.v1 as components

def render_flow_ui():
    st.subheader("Flow Control")

    # Load HTML file path
    html_path = os.path.join(os.path.dirname(__file__), "flow_split.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Render the flow editor layout
    components.html(html_content, height=600, scrolling=False)
