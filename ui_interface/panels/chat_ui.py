import streamlit as st

def render_chat_ui():
    st.subheader("Chat Interface")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for role, message in st.session_state.chat_history:
        st.markdown(f"**{role.capitalize()}**: {message}")
    user_input = st.text_input("Type your message")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("system", f"Echo: {user_input}"))
        st.experimental_rerun()
