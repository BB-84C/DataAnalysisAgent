import streamlit as st

from ui_interface.panels.namespace_manager_ui import render_namespace_manager_ui

from ui_interface.panels.flow_control.flow_ui import render_flow_ui
from ui_interface.panels.chat_ui import render_chat_ui
from ui_interface.panels.workspace_ui import render_workspace_ui
from ui_interface.panels.settings_ui import render_settings_ui 

# # Initial/default height of flow panel
# if "flow_panel_height" not in st.session_state:
#     st.session_state.flow_panel_height = 600

st.set_page_config(layout="wide")
st.title("Data Analysis Agent")

# Top area: flow editor + control + chat
top_left, top_right = st.columns([2, 1])

with top_left:
    render_flow_ui()

with top_right:
    render_chat_ui()
    st.divider()
    render_settings_ui()

# st.markdown("---")
# st.markdown("Adjust Flow Panel Height")
# st.slider("Flow Panel Height (px)", 300, 1200, key="flow_panel_height")
# st.markdown("---")

# Bottom area: workspace
st.divider()
bottom_left, bottom_right = st.columns([1, 1]) 
with bottom_left:
    render_workspace_ui()
with bottom_right:
    render_namespace_manager_ui()

# Split workspace in half and the other half to be log: agent decided to parse xx to xx, current runtime, etc. 
# token statistic
