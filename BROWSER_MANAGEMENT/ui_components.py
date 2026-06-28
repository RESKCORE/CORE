from __future__ import annotations
import streamlit as st
from typing import List, Tuple, Optional
from browser import BrowserApp
from utils import format_url_display, to_csv


def render_sidebar(browser: BrowserApp) -> None:
    with st.sidebar:
        st.markdown(
            "<h1 style='text-align: center; background: linear-gradient(90deg, #4CAF50, #2196F3); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🌐 Browser History<br>Manager</h1>",
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

        st.divider()
        total = browser.total_count
        pos = browser.get_position()
        if total > 0:
            st.progress((pos + 1) / total, text=f"Page {pos + 1} of {total}")
        else:
            st.progress(0.0, text="No pages")


def render_action_buttons(browser: BrowserApp) -> dict:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        visit = st.button("🔗 Visit", use_container_width=True)
    with col2:
        back = st.button("◀ Back", use_container_width=True, disabled=not browser.can_go_back())
    with col3:
        fwd = st.button("Forward ▶", use_container_width=True, disabled=not browser.can_go_forward())
    with col4:
        search = st.button("🔍 Search", use_container_width=True)
    with col5:
        delete = st.button("🗑️ Delete", use_container_width=True)
    with col6:
        clear_fwd = st.button("⏩ Del Fwd", use_container_width=True, disabled=not browser.can_go_forward())
    return {"visit": visit, "back": back, "forward": fwd, "search": search, "delete": delete, "clear_fwd": clear_fwd}


def render_url_input() -> str:
    return st.text_input(
        "Website URL",
        placeholder="e.g. https://google.com or google.com",
        label_visibility="collapsed",
    )


def handle_navigation(browser: BrowserApp, actions: dict, url_input: str) -> None:
    if actions["visit"] and url_input:
        success = browser.visit(url_input)
        if not success:
            st.warning("⚠️ Invalid or duplicate URL. Please enter a valid web address.")
        st.rerun()
    if actions["back"]:
        browser.back()
        st.rerun()
    if actions["forward"]:
        browser.forward()
        st.rerun()
    if actions["clear_fwd"]:
        browser.delete_forward_history()
        st.rerun()


def render_stats(browser: BrowserApp) -> None:
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📋 Total Pages", browser.total_count)
    with c2:
        pos = browser.get_position() + 1 if browser.total_count > 0 else 0
        st.metric("📍 Current Position", pos)
    with c3:
        st.metric("⬅️ Can Go Back", "Yes" if browser.can_go_back() else "No")
    with c4:
        st.metric("➡️ Can Go Forward", "Yes" if browser.can_go_forward() else "No")


def render_current_page(browser: BrowserApp) -> None:
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


def render_linked_list_viz(browser: BrowserApp) -> None:
    st.divider()
    st.subheader("🔗 Linked List Visualization")
    history_data = browser.show_history()
    if history_data:
        nodes_html = ""
        for idx, (url, is_current) in enumerate(history_data):
            label = format_url_display(url, 20)
            if is_current:
                nodes_html += (
                    '<span style="background:#4CAF50; color:white; padding:10px 16px; '
                    'border-radius:8px; font-weight:bold; margin:4px; border:2px solid #81C784;">'
                    f"📍 {label}</span>"
                )
            else:
                nodes_html += (
                    '<span style="background:#262730; color:#ccc; padding:10px 16px; '
                    'border-radius:8px; margin:4px; border:1px solid #555;">'
                    f"{label}</span>"
                )
            if idx < len(history_data) - 1:
                nodes_html += '<span style="color:#888; margin:0 4px; font-size:24px;"> ⇄ </span>'

        st.markdown(
            f'<div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:center; '
            f'padding:16px; background:#0e1117; border-radius:12px; border:1px solid #333; '
            f'min-height:80px;">{nodes_html}</div>',
            unsafe_allow_html=True,
        )
        st.caption("📍 Green highlighted node = current page | ⇄ bidirectional links")
    else:
        st.info("🔗 No nodes to display.")


def render_history_table(browser: BrowserApp) -> List[Tuple[str, bool]]:
    st.divider()
    st.subheader("📜 History")
    history_data = browser.show_history()
    if history_data:
        for idx, (url, is_current) in enumerate(history_data):
            marker = "📍 **← You are here**" if is_current else ""
            c1, c2, c3 = st.columns([1, 7, 2])
            with c1:
                st.write(f"**{idx + 1}**")
            with c2:
                st.write(url)
            with c3:
                st.write(marker)
    else:
        st.info("📭 No history available.")
    return history_data


def render_export(browser: BrowserApp, history_data: List[Tuple[str, bool]]) -> None:
    if history_data:
        st.divider()
        st.subheader("📥 Export History")
        export_data = [
            {"position": i + 1, "url": url, "is_current": is_current}
            for i, (url, is_current) in enumerate(history_data)
        ]
        csv_data = to_csv(export_data)
        st.download_button(
            "📥 Download CSV",
            data=csv_data,
            file_name="browser_history.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_search(browser: BrowserApp) -> None:
    st.divider()
    st.subheader("🔍 Search History")
    search_query = st.text_input(
        "Search query",
        placeholder="Type a URL or keyword to search...",
        label_visibility="collapsed",
        key="search_input",
    )
    if search_query:
        results = browser.search(search_query)
        if results:
            st.success(f"Found {len(results)} matching page(s)")
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
            st.warning("🔍 No results found.")


def render_delete_selected(browser: BrowserApp, history_data: List[Tuple[str, bool]], delete_clicked: bool) -> None:
    if history_data and delete_clicked:
        urls_for_select = [url for url, _ in history_data]
        selected = st.selectbox("Select a page to delete", urls_for_select)
        if selected:
            browser.delete_page(selected)
            st.success(f"Deleted: {selected}")
            st.rerun()


def render_database_status(browser: BrowserApp) -> None:
    st.divider()
    with st.expander("🗄️ Database Status", expanded=False):
        db_count = browser.get_db_record_count()
        c1, c2, c3 = st.columns(3)
        c1.metric("📁 Database", "browser_history.db")
        c2.metric("📊 Records in DB", db_count)
        c3.metric("📋 Linked List Size", browser.total_count)
        if st.button("🔄 Sync Database", use_container_width=True):
            browser.sync_database()
            st.success("Database synced!")
