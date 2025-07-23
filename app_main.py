import streamlit as st
from ui_interface.panels.flow_control.flow_ui import render_flow_ui
from ui_interface.panels.chat_ui import render_chat_ui
from ui_interface.panels.workspace_ui import render_workspace_ui

# # Initial/default height of flow panel
# if "flow_panel_height" not in st.session_state:
#     st.session_state.flow_panel_height = 600

st.set_page_config(layout="wide")
st.title("Data Analysis Agent")

# Top area: flow editor + control + chat
top_left, top_right = st.columns([3, 1])

with top_left:
    render_flow_ui()

with top_right:
    render_chat_ui()

# st.markdown("---")
# st.markdown("Adjust Flow Panel Height")
# st.slider("Flow Panel Height (px)", 300, 1200, key="flow_panel_height")
# st.markdown("---")

# Bottom area: workspace
st.divider()
render_workspace_ui()
