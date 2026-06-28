from __future__ import annotations
import streamlit as st
from typing import List
from collections import Counter


def render_reports(patients: List[dict], doctors: List[dict], appointments: List[dict]) -> None:
    st.title("📊 Reports & Analytics")
    st.caption("Hospital statistics and data visualizations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧬 Blood Group Distribution")
        blood_groups = Counter(p.get("blood_group", "Unknown") for p in patients)
        if blood_groups:
            labels = list(blood_groups.keys())
            values = list(blood_groups.values())
            st.bar_chart({"Blood Group": labels, "Count": values}, x="Blood Group", y="Count")
        else:
            st.info("No data available")

    with col2:
        st.subheader("📂 Department Distribution")
        departments = Counter(d.get("department", "Unknown") for d in doctors)
        if departments:
            labels = list(departments.keys())
            values = list(departments.values())
            st.bar_chart({"Department": labels, "Count": values}, x="Department", y="Count")
        else:
            st.info("No data available")

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("👤 Age Distribution")
        ages = [p.get("age", 0) or 0 for p in patients]
        if ages:
            bins = {"0-18": 0, "19-35": 0, "36-50": 0, "51-70": 0, "70+": 0}
            for a in ages:
                try:
                    a = int(a)
                    if a <= 18:
                        bins["0-18"] += 1
                    elif a <= 35:
                        bins["19-35"] += 1
                    elif a <= 50:
                        bins["36-50"] += 1
                    elif a <= 70:
                        bins["51-70"] += 1
                    else:
                        bins["70+"] += 1
                except (ValueError, TypeError):
                    pass
            st.bar_chart({"Age Range": list(bins.keys()), "Count": list(bins.values())}, x="Age Range", y="Count")
        else:
            st.info("No data available")

    with col4:
        st.subheader("👨‍⚕️ Doctor Workload")
        doc_appts = Counter(a.get("doctor_name", "Unknown") for a in appointments)
        if doc_appts:
            labels = list(doc_appts.keys())
            values = list(doc_appts.values())
            st.bar_chart({"Doctor": labels, "Appointments": values}, x="Doctor", y="Appointments")
        else:
            st.info("No data available")

    st.divider()
    st.subheader("📊 Key Metrics")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("👤 Total Patients", len(patients))
    with col6:
        st.metric("👨‍⚕️ Total Doctors", len(doctors))
    with col7:
        st.metric("📅 Total Appointments", len(appointments))
    with col8:
        waiting = sum(1 for a in appointments if a.get("status") == "waiting")
        st.metric("⏳ Waiting", waiting)
