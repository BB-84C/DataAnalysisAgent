# ui_interface/panels/namespace_manager_ui.py
# ui_interface/panels/namespace_manager_ui.py
import streamlit as st
import logging
from ui_interface.ns_log_bus import LOG_QUEUE
from streamlit_autorefresh import st_autorefresh

# 统一 formatter（只在 UI 侧格式化）
_FORMATTER = logging.Formatter(
    "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

def _drain_queue_into_session_state():
    """只在主线程（UI 渲染）里把队列里的日志刷进 session_state。"""
    buf = st.session_state.setdefault("ns_logs", [])
    # 非阻塞地把当前所有日志取空
    while True:
        try:
            rec = LOG_QUEUE.get_nowait()
        except Exception:
            break
        else:
            buf.append(_FORMATTER.format(rec))

def render_namespace_manager_ui():
    # 每次渲染先把新日志拉入缓存
    _drain_queue_into_session_state()

    st.subheader("Namespace Manager Panel")
    
    c0, c1 = st.columns([0.45, 0.55])
    with c0:
        auto = st.toggle("Auto refresh", value=True, key="ns_auto_refresh")
    with c1:
        interval_ms = st.slider("Interval (ms)", 500, 5000, 1500, 100, key="ns_refresh_interval")

    # 只在本面板里挂 ONE 个定时器（避免全局多次调用）
    if auto:
        st_autorefresh(interval=int(interval_ms), key="ns_autorefresh_timer")

    # 控制栏
    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Refresh"):
            # 手动刷新就再拉一遍（通常没必要，因为上面每次渲染已拉取）
            _drain_queue_into_session_state()
            st.rerun()
    with c2:
        if st.button("Clear"):
            st.session_state["ns_logs"] = []
            st.rerun()
    with c3:
        tail_n = st.number_input("Tail lines", min_value=100, max_value=5000, value=500, step=100)

    # 展示尾部 N 行
    logs = st.session_state.get("ns_logs", [])
    # st.code("\n".join(logs[-int(tail_n):]) if logs else "(no logs yet)", language="text")
    text = "\n".join(logs[-int(tail_n):]) if logs else "(no logs yet)"
    st.text_area(
        label="Namespace Manager Logs",
        value=text,
        height=440,
        key="ns_logs_view",
        label_visibility="collapsed",
        disabled=False,              # 只读
    )


