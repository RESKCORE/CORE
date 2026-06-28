"""
app.py
-------
Main Streamlit entry point for the Browser History Manager.

This module is responsible ONLY for the user interface: rendering the
sidebar, buttons, cards, tables, and the linked-list visualization.
All actual logic (navigation, persistence, validation) lives in
`browser.py`, `linked_list.py`, and `database.py`.

Run with:
    streamlit run app.py

Author: Reddy Santosh Kumar
"""

import streamlit as st

from browser import BrowserApp, DuplicateVisitError, EmptyHistoryError, InvalidURLError
from utils import extract_display_name, format_timestamp

# ----------------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="PathWeaver — Browser History Manager",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# THEME — "Circuit Trail" design system
# A dark, schematic, PCB-trace inspired theme: the browsing path is
# drawn like a circuit trace, with nodes as solder points and the
# active page glowing like a powered component. This is deliberately
# NOT a generic blue/gray dashboard -- it reflects the linked-list
# wiring at the heart of the project.
# ----------------------------------------------------------------------

CIRCUIT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-deep: #0b0f0e;
        --bg-panel: #111715;
        --trace-copper: #c97b4e;
        --trace-glow: #7CFFB2;
        --trace-dim: #2c3a35;
        --ink: #e8f1ec;
        --ink-dim: #8aa39a;
        --danger: #ff6b6b;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #121a17 0%, var(--bg-deep) 55%);
        color: var(--ink);
        font-family: 'JetBrains Mono', monospace;
    }

    h1, h2, h3, .pw-display {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }

    section[data-testid="stSidebar"] {
        background: var(--bg-panel);
        border-right: 1px solid var(--trace-dim);
    }

    .pw-eyebrow {
        color: var(--trace-glow);
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .pw-card {
        background: var(--bg-panel);
        border: 1px solid var(--trace-dim);
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }

    .pw-current-card {
        background: linear-gradient(135deg, rgba(124,255,178,0.10), rgba(201,123,78,0.06));
        border: 1px solid var(--trace-glow);
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 0 24px rgba(124,255,178,0.08);
    }

    .pw-url {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--ink);
        word-break: break-all;
    }

    .pw-timestamp {
        color: var(--ink-dim);
        font-size: 0.82rem;
        margin-top: 4px;
    }

    .pw-node {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid var(--trace-dim);
        background: var(--bg-panel);
        color: var(--ink-dim);
        font-size: 0.88rem;
        white-space: nowrap;
    }

    .pw-node-current {
        border: 1px solid var(--trace-glow);
        color: var(--trace-glow);
        background: rgba(124,255,178,0.08);
        font-weight: 700;
        box-shadow: 0 0 12px rgba(124,255,178,0.25);
    }

    .pw-arrow {
        color: var(--trace-copper);
        font-size: 1.1rem;
        margin: 0 2px;
    }

    .pw-divider {
        border-top: 1px dashed var(--trace-dim);
        margin: 18px 0;
    }

    .pw-status-ok {
        color: var(--trace-glow);
        font-weight: 700;
    }

    .pw-status-bad {
        color: var(--danger);
        font-weight: 700;
    }

    div.stButton > button {
        background: var(--bg-panel);
        color: var(--ink);
        border: 1px solid var(--trace-dim);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        transition: all 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: var(--trace-glow);
        color: var(--trace-glow);
    }

    div.stButton > button:disabled {
        opacity: 0.35;
    }
</style>
"""

st.markdown(CIRCUIT_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------------------------

def get_app() -> BrowserApp:
    """
    Retrieve the singleton BrowserApp instance for this Streamlit
    session, creating it (and loading history from SQLite) only once
    per session.

    Returns:
        BrowserApp: The controller managing linked-list + database state.
    """
    if "browser_app" not in st.session_state:
        st.session_state.browser_app = BrowserApp()
    return st.session_state.browser_app


app = get_app()

# Holds the most recent user-facing status message (success/error/info).
if "pw_message" not in st.session_state:
    st.session_state.pw_message = None


def flash(kind: str, text: str) -> None:
    """
    Queue a one-shot status message to display at the top of the main
    area after the next rerun.

    Args:
        kind (str): One of "success", "error", "info", "warning".
        text (str): The message text to display.
    """
    st.session_state.pw_message = (kind, text)


# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="pw-eyebrow">PROJECT</div>', unsafe_allow_html=True)
    st.markdown("### 🧭 PathWeaver")
    st.caption("Browser History Manager · Doubly Linked List Edition")

    st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

    current_node = app.show_current()
    st.markdown('<div class="pw-eyebrow">CURRENT PAGE</div>', unsafe_allow_html=True)
    if current_node:
        st.markdown(f"**{extract_display_name(current_node.url)}**")
        st.caption(current_node.url)
    else:
        st.caption("No page open yet")

    st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

    st.metric("Total History Count", app.get_total_count())

    st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear History", use_container_width=True):
        app.clear_history()
        flash("success", "History cleared successfully.")
        st.rerun()

    st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

    db_ok = app.is_database_connected()
    status_class = "pw-status-ok" if db_ok else "pw-status-bad"
    status_text = "● CONNECTED" if db_ok else "● DISCONNECTED"
    st.markdown('<div class="pw-eyebrow">DATABASE STATUS</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="{status_class}">{status_text}</span>', unsafe_allow_html=True)
    st.caption(f"browser_history.db · {app.get_db_row_count()} row(s) persisted")


# ----------------------------------------------------------------------
# MAIN AREA — HEADER
# ----------------------------------------------------------------------

st.markdown('<div class="pw-eyebrow">EDUCATIONAL DEMO</div>', unsafe_allow_html=True)
st.title("🧭 PathWeaver — Browser History Manager")
st.caption(
    "A working simulation of Chrome/Edge-style history navigation, "
    "built entirely on a Doubly Linked List, with SQLite persistence."
)

# Display any queued flash message.
if st.session_state.pw_message:
    kind, text = st.session_state.pw_message
    getattr(st, kind)(text)
    st.session_state.pw_message = None

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# NAVIGATION CONTROLS
# ----------------------------------------------------------------------

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 2, 1])

with nav_col1:
    if st.button("◀ Back", use_container_width=True, disabled=not app.can_go_back()):
        try:
            app.back()
            flash("success", "Moved back in history.")
        except EmptyHistoryError as error:
            flash("error", str(error))
        st.rerun()

with nav_col2:
    if st.button("Forward ▶", use_container_width=True, disabled=not app.can_go_forward()):
        try:
            app.forward()
            flash("success", "Moved forward in history.")
        except EmptyHistoryError as error:
            flash("error", str(error))
        st.rerun()

with nav_col3:
    with st.form(key="visit_form", clear_on_submit=True):
        url_input_col, visit_button_col = st.columns([4, 1])
        with url_input_col:
            url_input = st.text_input(
                "Website URL",
                placeholder="e.g. github.com or https://chatgpt.com",
                label_visibility="collapsed",
            )
        with visit_button_col:
            visit_submitted = st.form_submit_button("🌐 Visit", use_container_width=True)

    if visit_submitted:
        try:
            new_node = app.visit(url_input)
            flash("success", f"Visited {new_node.url}")
        except InvalidURLError as error:
            flash("error", str(error))
        except DuplicateVisitError as error:
            flash("warning", str(error))
        st.rerun()

with nav_col4:
    if st.button("🧹 Clear All", use_container_width=True):
        app.clear_history()
        flash("success", "History cleared successfully.")
        st.rerun()

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CURRENT PAGE CARD
# ----------------------------------------------------------------------

st.subheader("📍 Current Page")

current_node = app.show_current()
if current_node:
    st.markdown(
        f"""
        <div class="pw-current-card">
            <div class="pw-eyebrow">NOW VIEWING</div>
            <div class="pw-url">{current_node.url}</div>
            <div class="pw-timestamp">Visited: {format_timestamp(current_node.visited_time)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("No page is currently open. Visit a website to begin browsing.")

# Current Position Indicator
all_nodes = app.show_history()
if all_nodes and current_node:
    position = all_nodes.index(current_node) + 1
    total = len(all_nodes)
    st.caption(f"📌 Position **{position}** of **{total}** in history")
    st.progress(position / total if total else 0)

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# LINKED LIST VISUALIZATION
# ----------------------------------------------------------------------

st.subheader("🔗 Doubly Linked List Visualization")
st.caption("Each node below is one visited page. The glowing node is `current`. Arrows show `prev ⇄ next` links.")

nodes = app.show_history()
if not nodes:
    st.caption("_(empty list — no nodes yet)_")
else:
    html_parts = []
    for index, node in enumerate(nodes):
        is_current = node is current_node
        css_class = "pw-node pw-node-current" if is_current else "pw-node"
        marker = "🟢 " if is_current else ""
        html_parts.append(f'<span class="{css_class}">{marker}{extract_display_name(node.url)}</span>')
        if index < len(nodes) - 1:
            html_parts.append('<span class="pw-arrow">⇄</span>')

    st.markdown(
        f'<div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:14px 0;">{"".join(html_parts)}</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SEARCH
# ----------------------------------------------------------------------

st.subheader("🔍 Search History")
search_col1, search_col2 = st.columns([4, 1])
with search_col1:
    search_query = st.text_input(
        "Search keyword",
        placeholder="Type part of a URL, e.g. 'github'",
        label_visibility="collapsed",
        key="search_box",
    )
with search_col2:
    search_clicked = st.button("Search", use_container_width=True, key="search_button")

if search_clicked or search_query:
    results = app.search(search_query) if search_query else []
    if search_query and not results:
        st.warning(f"No pages found matching '{search_query}'.")
    elif results:
        st.success(f"Found {len(results)} matching page(s).")
        for node in results:
            with st.expander(f"🔸 {node.url}"):
                st.caption(f"Visited: {format_timestamp(node.visited_time)}")
                if st.button("Delete this page", key=f"del_search_{id(node)}"):
                    try:
                        app.delete_page(node)
                        flash("success", f"Deleted {node.url}")
                    except EmptyHistoryError as error:
                        flash("error", str(error))
                    st.rerun()

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# HISTORY TABLE + DELETE SELECTED
# ----------------------------------------------------------------------

st.subheader("📋 Full History Table")

nodes = app.show_history()
if not nodes:
    st.caption("_(no history to display)_")
else:
    table_rows = []
    for index, node in enumerate(nodes):
        table_rows.append(
            {
                "Position": index + 1,
                "URL": node.url,
                "Visited Time": format_timestamp(node.visited_time),
                "Current": "✅" if node is current_node else "",
            }
        )
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    delete_col1, delete_col2 = st.columns([4, 1])
    with delete_col1:
        options = [f"{i + 1}. {n.url}" for i, n in enumerate(nodes)]
        selected_label = st.selectbox(
            "Select a page to delete",
            options=options,
            label_visibility="collapsed",
        )
    with delete_col2:
        if st.button("🗑️ Delete Selected", use_container_width=True):
            selected_index = options.index(selected_label)
            target_node = nodes[selected_index]
            try:
                app.delete_page(target_node)
                flash("success", f"Deleted '{target_node.url}' from history.")
            except EmptyHistoryError as error:
                flash("error", str(error))
            st.rerun()

st.markdown('<div class="pw-divider"></div>', unsafe_allow_html=True)
st.caption("PathWeaver · Built to demonstrate Doubly Linked List internals · SQLite-backed persistence")
