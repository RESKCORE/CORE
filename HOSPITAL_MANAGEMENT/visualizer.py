from __future__ import annotations
import streamlit as st
from typing import Optional
from linked_list import SinglyLinkedList, DoublyLinkedList, CircularLinkedList, Queue


def render_linked_list_viz(ll_type: str, items: list, current_idx: int = -1, circular: bool = False) -> None:
    if not items:
        st.info(f"🔗 No nodes in the {ll_type}.")
        return

    nodes_html = ""
    for i, item in enumerate(items):
        label = _get_label(item)
        is_current = (i == current_idx)
        bg = "#4CAF50" if is_current else "#262730"
        border = "2px solid #4CAF50" if is_current else "1px solid #555"
        text_color = "white" if is_current else "#ccc"
        extra = "📍" if is_current else ""
        nodes_html += f'<span style="background:{bg}; color:{text_color}; padding:8px 14px; border-radius:8px; font-weight:bold; margin:4px; border:{border};">{extra} {label}</span>'

        arrow = " ⇄ " if ll_type == "Doubly Linked List" else " → "
        if i < len(items) - 1:
            nodes_html += f'<span style="color:#888; margin:0 4px; font-size:20px;">{arrow}</span>'

    if circular and items:
        nodes_html += f'<span style="color:#888; margin:0 4px; font-size:20px;"> → </span>'
        nodes_html += f'<span style="background:#FF9800; color:white; padding:6px 10px; border-radius:50%; font-size:14px;">↻</span>'

    st.markdown(
        f'<div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:center; padding:16px; background:#0e1117; border-radius:12px; border:1px solid #333;">{nodes_html}</div>',
        unsafe_allow_html=True,
    )

    if current_idx >= 0 and current_idx < len(items):
        st.caption(f"📍 Current node at position {current_idx + 1} of {len(items)}")


def _get_label(item) -> str:
    name = item.get("name") or item.get("patient_name") or item.get("diagnosis") or str(item.get("patient_id", ""))
    name = str(name)
    if len(name) > 20:
        name = name[:17] + "..."
    return name


def render_patient_viz(sll: SinglyLinkedList) -> None:
    items = sll.to_list()
    st.subheader("🔗 Patient Records (Singly Linked List)")
    st.caption("Head → Patient1 → Patient2 → ... → PatientN → None")
    render_linked_list_viz("Singly Linked List", items)


def render_medical_viz(dll: DoublyLinkedList) -> None:
    items = dll.to_list()
    pos = dll.current_position()
    st.subheader("🔗 Medical History (Doubly Linked List)")
    st.caption("Visit1 ⇄ Visit2 ⇄ Visit3 ⇄ ... ⇄ VisitN")
    render_linked_list_viz("Doubly Linked List", items, pos)


def render_doctor_viz(cll: CircularLinkedList) -> None:
    items = cll.to_list()
    current = cll.current_data()
    current_id = current.get("doctor_id") if current else None
    pos = -1
    for i, d in enumerate(items):
        if d.get("doctor_id") == current_id:
            pos = i
            break
    st.subheader("🔗 Doctor Duty Rotation (Circular Linked List)")
    st.caption("DrA → DrB → DrC → DrA (tail points back to head)")
    render_linked_list_viz("Circular Linked List", items, pos, circular=True)


def render_appointment_viz(queue: Queue) -> None:
    items = queue.to_list()
    st.subheader("🔗 Appointment Queue (Linked List Queue)")
    st.caption("Front → Appt1 → Appt2 → ... → ApptN → Rear")
    render_linked_list_viz("Queue", items)
