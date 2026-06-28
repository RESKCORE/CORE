import streamlit as st
from browser import BrowserApp
from utils import format_url_display

st.set_page_config(page_title="Browser History Manager", layout="wide")

if "browser" not in st.session_state:
    st.session_state.browser = BrowserApp()

browser: BrowserApp = st.session_state.browser

# ── Sidebar ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<h1 style='text-align: center;'>🌐 Browser History<br>Manager</h1>",
        unsafe_allow_html=True,
    )
    st.divider()

    current = browser.show_current()
    st.markdown("**📍 Current Page**")
    if current:
        st.info(format_url_display(current, 35))
    else:
        st.info("No page loaded")

    st.metric(label="📊 Total History Count", value=browser.total_count)

    st.divider()

    if st.button("🗑️ Clear History", use_container_width=True, type="primary"):
        browser.clear_history()
        st.rerun()

# ── Main Area ───────────────────────────────────────────────────────────

st.title("🌐 Browser History Manager")
st.caption("A doubly linked list demonstration using Streamlit + SQLite")

# ── Action Buttons ──────────────────────────────────────────────────────

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    visit_clicked = st.button("🔗 Visit Website", use_container_width=True)
with col2:
    back_clicked = st.button("◀ Back", use_container_width=True, disabled=not browser.can_go_back())
with col3:
    forward_clicked = st.button("Forward ▶", use_container_width=True, disabled=not browser.can_go_forward())
with col4:
    search_clicked = st.button("🔍 Search", use_container_width=True)
with col5:
    delete_sel_clicked = st.button("🗑️ Delete Selected", use_container_width=True)
with col6:
    clear_fwd = st.button("⏩ Delete Forward", use_container_width=True, disabled=not browser.can_go_forward())

# ── URL Input ───────────────────────────────────────────────────────────

url_input = st.text_input(
    "Website URL",
    placeholder="e.g. https://google.com or google.com",
    label_visibility="collapsed",
)

if visit_clicked and url_input:
    success = browser.visit(url_input)
    if not success:
        st.warning("⚠️ Invalid or duplicate URL. Please enter a valid web address.")
    st.rerun()

if back_clicked:
    browser.back()
    st.rerun()

if forward_clicked:
    browser.forward()
    st.rerun()

if clear_fwd:
    browser.delete_forward_history()
    st.rerun()

# ── Current Page Card ───────────────────────────────────────────────────

st.divider()
st.subheader("📌 Current Page")

current = browser.show_current()
if current:
    cols = st.columns([1, 5, 1])
    with cols[1]:
        st.markdown(
            f"""
            <div style="border:2px solid #4CAF50; border-radius:12px; padding:20px; text-align:center; background:#0e1117;">
                <h3 style="margin:0; color:#4CAF50;">🌍 {format_url_display(current, 60)}</h3>
                <p style="margin:8px 0 0 0; color:#888;">Position {browser.get_position() + 1} of {browser.total_count}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("💡 No page loaded. Visit a website to get started.")

# ── History Table ───────────────────────────────────────────────────────

st.divider()
st.subheader("📜 History")

history_data = browser.show_history()
if history_data:
    rows = []
    for idx, (url, is_current) in enumerate(history_data):
        marker = "📍 **← You are here**" if is_current else ""
        rows.append({"#": idx + 1, "URL": url, "Status": marker})

    # Build clickable table
    for r in rows:
        c1, c2, c3 = st.columns([1, 7, 2])
        with c1:
            st.write(f"**{r['#']}**")
        with c2:
            st.write(r["URL"])
        with c3:
            st.write(r["Status"])
else:
    st.info("📭 No history available.")

# ── Current Position Indicator ──────────────────────────────────────────

st.divider()
st.subheader("📍 Position Indicator")

total = browser.total_count
pos = browser.get_position()
if total > 0:
    progress = (pos + 1) / total
    st.progress(progress, text=f"Page {pos + 1} of {total}")
else:
    st.progress(0.0, text="No pages")

# ── Linked List Visualization ───────────────────────────────────────────

st.divider()
st.subheader("🔗 Linked List Visualization")

history_data = browser.show_history()
if history_data:
    nodes_html = ""
    for idx, (url, is_current) in enumerate(history_data):
        label = format_url_display(url, 25)
        if is_current:
            nodes_html += f'<span style="background:#4CAF50; color:white; padding:8px 14px; border-radius:8px; font-weight:bold; margin:4px;">📍 {label}</span>'
        else:
            nodes_html += f'<span style="background:#262730; color:#ccc; padding:8px 14px; border-radius:8px; margin:4px;">{label}</span>'
        if idx < len(history_data) - 1:
            nodes_html += '<span style="color:#888; margin:0 4px; font-size:20px;"> ⇄ </span>'

    st.markdown(
        f'<div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:center; padding:16px; background:#0e1117; border-radius:12px; border:1px solid #333;">{nodes_html}</div>',
        unsafe_allow_html=True,
    )
else:
    st.info("🔗 No nodes to display.")

# ── Search ──────────────────────────────────────────────────────────────

st.divider()
st.subheader("🔍 Search History")

search_query = st.text_input("Search query", placeholder="Type a URL or keyword...", label_visibility="collapsed")

if search_query:
    results = browser.search(search_query)
    if results:
        for idx, url, is_current in results:
            cols = st.columns([1, 7, 2])
            with cols[0]:
                st.write(f"**{idx + 1}**")
            with cols[1]:
                st.write(url)
            with cols[2]:
                if is_current:
                    st.write("📍 **Current**")
                else:
                    st.write("")
    else:
        st.warning("🔍 No results found.")

# ── Delete Selected ─────────────────────────────────────────────────────

if history_data and delete_sel_clicked:
    urls_for_select = [url for url, _ in history_data]
    selected = st.selectbox("Select a page to delete", urls_for_select)
    if selected:
        browser.delete_page(selected)
        st.success(f"Deleted: {selected}")
        st.rerun()

# ── Database Status ─────────────────────────────────────────────────────

st.divider()
with st.expander("🗄️ Database Status", expanded=False):
    db_count = browser.get_db_record_count()
    c1, c2, c3 = st.columns(3)
    c1.metric("📁 Database", "browser_history.db")
    c2.metric("📊 Records in DB", db_count)
    c3.metric("📋 Linked List Size", browser.total_count)
    if st.button("🔄 Sync Database"):
        browser.sync_database()
        st.success("Database synced!")
