from __future__ import annotations
import streamlit as st
from patient import PatientManager
from doctor import DoctorManager
from appointment import AppointmentManager


def render_dashboard(pm: PatientManager, dm: DoctorManager, am: AppointmentManager) -> None:
    st.title("🏥 Hospital Dashboard")
    st.caption("Real-time overview of hospital operations")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Total Patients", pm.count)
    with col2:
        st.metric("👨‍⚕️ Total Doctors", dm.count)
    with col3:
        st.metric("📅 Appointments Waiting", am.count)
    with col4:
        current_doc = dm.current_doctor()
        doc_name = current_doc.get("name", "N/A") if current_doc else "N/A"
        st.metric("🔄 Doctor On Duty", doc_name)

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Recent Patients")
        patients = pm.get_all_patients()[:5]
        if patients:
            for p in patients:
                with st.container():
                    st.markdown(
                        f"<div style='padding:8px; border:1px solid #333; border-radius:8px; margin:4px 0;'>"
                        f"<strong>{p.get('name', '')}</strong> | {p.get('age', '')} yrs | {p.get('blood_group', '')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No patients registered yet")

    with col_right:
        st.subheader("📅 Appointment Queue")
        queue = am.get_queue()[:5]
        if queue:
            for i, a in enumerate(queue):
                with st.container():
                    st.markdown(
                        f"<div style='padding:8px; border:1px solid #333; border-radius:8px; margin:4px 0;'>"
                        f"<strong>#{i + 1}</strong> {a.get('patient_name', '')} → {a.get('doctor_name', '')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No appointments in queue")

    st.divider()
    st.subheader("🔄 Doctor Duty Rotation")
    doctors = dm.get_all_doctors()
    if doctors:
        current = dm.current_doctor()
        current_id = current.get("doctor_id") if current else None
        cols = st.columns(len(doctors))
        for idx, (col, doc) in enumerate(zip(cols, doctors)):
            is_current = doc.get("doctor_id") == current_id
            border = "2px solid #4CAF50" if is_current else "1px solid #333"
            bg = "#1a3a1a" if is_current else "#0e1117"
            with col:
                st.markdown(
                    f"<div style='border:{border}; border-radius:8px; padding:10px; text-align:center; background:{bg};'>"
                    f"<p style='font-weight:bold; margin:0;'>{doc.get('name', '')}</p>"
                    f"<p style='font-size:12px; margin:0; color:#888;'>{doc.get('department', '')}</p>"
                    f"<p style='font-size:11px; margin:0; color:#666;'>{'⭐ ON DUTY' if is_current else ''}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("No doctors registered yet")
