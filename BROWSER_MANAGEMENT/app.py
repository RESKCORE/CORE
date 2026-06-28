import streamlit as st
from browser import BrowserApp
from ui_components import (
    render_sidebar,
    render_action_buttons,
    render_url_input,
    handle_navigation,
    render_stats,
    render_current_page,
    render_linked_list_viz,
    render_history_table,
    render_export,
    render_search,
    render_delete_selected,
    render_database_status,
)

st.set_page_config(page_title="Browser History Manager", page_icon="🌐", layout="wide")

if "browser" not in st.session_state:
    st.session_state.browser = BrowserApp()

browser: BrowserApp = st.session_state.browser

# ── Sidebar ─────────────────────────────────────────────────────────────

render_sidebar(browser)

# ── Header ──────────────────────────────────────────────────────────────

st.title("🌐 Browser History Manager")
st.caption("A doubly linked list demonstration using Streamlit + SQLite")

# ── Actions ─────────────────────────────────────────────────────────────

actions = render_action_buttons(browser)
url_input = render_url_input()
handle_navigation(browser, actions, url_input)

# ── Stats ───────────────────────────────────────────────────────────────

render_stats(browser)

# ── Current Page ────────────────────────────────────────────────────────

render_current_page(browser)

# ── Linked List Visualization ───────────────────────────────────────────

render_linked_list_viz(browser)

# ── History Table ───────────────────────────────────────────────────────

history_data = render_history_table(browser)

# ── Export ──────────────────────────────────────────────────────────────

render_export(browser, history_data)

# ── Search ──────────────────────────────────────────────────────────────

render_search(browser)

# ── Delete Selected ─────────────────────────────────────────────────────

render_delete_selected(browser, history_data, actions["delete"])

# ── Database Status ─────────────────────────────────────────────────────

render_database_status(browser)
