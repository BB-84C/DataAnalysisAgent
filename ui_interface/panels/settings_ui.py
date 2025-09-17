# ui_interface/panels/settings_ui.py
import os
import streamlit as st

_DEFAULT_TOOL_PY = r"/external_tools/STM_Lab/stm_lab_scripts_lib.py"
_DEFAULT_TOOL_SCHEMA = r"/external_tools/STM_Lab/stm_lab_script_lib_schema.json"
_DEFAULT_ROOT = r"D:/GPTAutoSTM"

def _ensure_state():
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "root_path": _DEFAULT_ROOT,
            "tool_py": _DEFAULT_TOOL_PY,
            "tool_schema": _DEFAULT_TOOL_SCHEMA,
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "api_generation": 0,
        }

def render_settings_ui():
    _ensure_state()
    st.subheader("Settings")

    # --- Inputs (no submit; immediate update) ---
    root_path = st.text_input(
        "Root Path",
        value=st.session_state.settings["root_path"],
        key="settings_root_path",
    )
    tool_py = st.text_input(
        "Tool Library (.py)",
        value=st.session_state.settings["tool_py"],
        key="settings_tool_py",
    )
    tool_schema = st.text_input(
        "Tool Schema (.json)",
        value=st.session_state.settings["tool_schema"],
        key="settings_tool_schema",
    )

    st.markdown("**OpenAI**")
    left, right = st.columns([4, 1], vertical_alignment="bottom")

    with left:
        openai_api_key = st.text_input(
            "OPENAI_API_KEY",
            value=st.session_state.settings["openai_api_key"],
            type="password",
            key="settings_openai_api_key",
        )

    with right:
        apply_clicked = st.button("Apply", type="primary", use_container_width=True, key="apply_api_btn")

    # Synchronize input fields to session in real time (but don't rebuild the client automatically)
    st.session_state.settings["openai_api_key"] = openai_api_key.strip()

    # Only clicking Apply triggers the rebuild of the client's "code" increment.
    if apply_clicked:
        st.session_state.settings["api_generation"] = st.session_state.settings.get("api_generation", 0) + 1
        st.success(f"API applied (gen = {st.session_state.settings['api_generation']}).")

    # --- Sync back to session_state + env (reactive on every rerun) ---
    st.session_state.settings["root_path"] = root_path.strip() or _DEFAULT_ROOT
    st.session_state.settings["tool_py"] = tool_py.strip() or _DEFAULT_TOOL_PY
    st.session_state.settings["tool_schema"] = tool_schema.strip() or _DEFAULT_TOOL_SCHEMA
    st.session_state.settings["openai_api_key"] = openai_api_key.strip()
    
    