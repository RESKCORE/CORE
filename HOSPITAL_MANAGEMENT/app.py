import streamlit as st
from database import DatabaseManager
from patient import PatientManager
from doctor import DoctorManager
from appointment import AppointmentManager
from medical_history import MedicalHistoryManager
from dashboard import render_dashboard
from reports import render_reports
from visualizer import render_patient_viz, render_medical_viz, render_doctor_viz, render_appointment_viz
from ai_assistant import AIAssistant
from search_engine import SearchEngine

st.set_page_config(page_title="Hospital Management System", page_icon="🏥", layout="wide")

# ── Initialize ──────────────────────────────────────────────────────────

if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()
if "pm" not in st.session_state:
    st.session_state.pm = PatientManager(st.session_state.db)
if "dm" not in st.session_state:
    st.session_state.dm = DoctorManager(st.session_state.db)
if "am" not in st.session_state:
    st.session_state.am = AppointmentManager(st.session_state.db)
if "mh" not in st.session_state:
    st.session_state.mh = MedicalHistoryManager(st.session_state.db)
if "ai" not in st.session_state:
    st.session_state.ai = AIAssistant()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

db = st.session_state.db
pm = st.session_state.pm
dm = st.session_state.dm
am = st.session_state.am
mh = st.session_state.mh
ai = st.session_state.ai

# ── Sidebar ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<h1 style='text-align:center; background: linear-gradient(90deg, #4CAF50, #2196F3); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🏥 Hospital<br>Management</h1>",
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👤 Patients",
            "👨‍⚕️ Doctors",
            "📅 Appointments",
            "📖 Medical History",
            "🔄 Doctor Rotation",
            "🤖 AI Health Assistant",
            "📊 Reports",
            "🔗 Linked List Viz",
            "🔍 Global Search",
            "⚙ Settings",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"👤 {pm.count} Patients  |  👨‍⚕️ {dm.count} Doctors  |  📅 {am.count} Queue")
    ai_status = "🟢 AI Ready" if ai.is_configured() else "🔴 AI Off"
    st.caption(f"{ai_status}")

# ── Pages ───────────────────────────────────────────────────────────────

# ──── Dashboard ─────────────────────────────────────────────────────────

if page == "🏠 Dashboard":
    render_dashboard(pm, dm, am, ai)

# ──── Patients ──────────────────────────────────────────────────────────

elif page == "👤 Patients":
    st.title("👤 Patient Management")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add", "🔍 Search", "📋 All Patients", "✏️ Update / Delete"])

    with tab1:
        with st.form("add_patient"):
            name = st.text_input("Full Name")
            age = st.number_input("Age", 0, 150, 30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Contact (10 digits)")
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            if st.form_submit_button("➕ Add Patient", use_container_width=True, type="primary"):
                if name and contact:
                    result = pm.add_patient(name, age, gender, contact, blood_group)
                    if result:
                        st.success(f"✅ Patient {name} added successfully! ID: {result['patient_id']}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add patient")
                else:
                    st.warning("⚠️ Name and Contact are required")

    with tab2:
        search_term = st.text_input("Search by name", placeholder="Enter patient name...", label_visibility="collapsed")
        if search_term:
            results = pm.search_by_name(search_term)
            if results:
                for r in results:
                    with st.expander(f"{r.get('name')} ({r.get('patient_id')})"):
                        st.json(r)
                        if ai.is_configured():
                            if st.button(f"✨ AI Summary for {r.get('name')}", key=f"sum_{r.get('patient_id')}"):
                                with st.spinner("Generating AI summary..."):
                                    visits = mh.get_history(r.get("patient_id"))
                                    summary = ai.generate_patient_summary(r, visits)
                                if summary:
                                    st.markdown(summary)
            else:
                st.warning("No patients found")

    with tab3:
        patients = pm.get_all_patients()
        if patients:
            st.dataframe(patients, use_container_width=True, hide_index=True)
        else:
            st.info("No patients registered yet")

    with tab4:
        patients_list = pm.get_all_patients()
        if patients_list:
            patient_options = {f"{p.get('patient_id')} - {p.get('name')}": p for p in patients_list}
            selected_label = st.selectbox("Select Patient", list(patient_options.keys()))
            selected = patient_options.get(selected_label)
            if selected:
                with st.form("update_patient"):
                    new_name = st.text_input("Name", selected.get("name", ""))
                    new_age = st.number_input("Age", 0, 150, selected.get("age", 30))
                    new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(selected.get("gender", "Male")))
                    new_contact = st.text_input("Contact", selected.get("contact", ""))
                    new_bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(selected.get("blood_group", "A+")))
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("✏️ Update", use_container_width=True):
                            pm.update_patient(selected["patient_id"], name=new_name, age=new_age, gender=new_gender, contact=new_contact, blood_group=new_bg)
                            st.success("✅ Patient updated!")
                            st.rerun()
                    with c2:
                        if st.form_submit_button("🗑️ Delete", use_container_width=True):
                            pm.delete_patient(selected["patient_id"])
                            st.success("🗑️ Patient deleted!")
                            st.rerun()
        else:
            st.info("No patients to manage")

# ──── Doctors ───────────────────────────────────────────────────────────

elif page == "👨‍⚕️ Doctors":
    st.title("👨‍⚕️ Doctor Management")
    tab1, tab2, tab3 = st.tabs(["➕ Add", "📋 All Doctors", "🗑️ Remove"])

    with tab1:
        with st.form("add_doctor"):
            name = st.text_input("Doctor Name")
            department = st.selectbox("Department", ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology", "Radiology", "Emergency", "General Medicine"])
            shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
            if st.form_submit_button("➕ Add Doctor", use_container_width=True, type="primary"):
                if name:
                    result = dm.add_doctor(name, department, shift)
                    if result:
                        st.success(f"✅ Dr. {name} added! ID: {result['doctor_id']}")
                        st.rerun()
                else:
                    st.warning("⚠️ Name is required")

    with tab2:
        doctors = dm.get_all_doctors()
        if doctors:
            st.dataframe(doctors, use_container_width=True, hide_index=True)
        else:
            st.info("No doctors registered")

    with tab3:
        doctors = dm.get_all_doctors()
        if doctors:
            doc_options = {f"{d.get('doctor_id')} - {d.get('name')}": d for d in doctors}
            selected = st.selectbox("Select Doctor to Remove", list(doc_options.keys()))
            if st.button("🗑️ Remove Doctor", use_container_width=True, type="primary"):
                doc = doc_options[selected]
                dm.remove_doctor(doc["doctor_id"])
                st.success(f"🗑️ {doc['name']} removed!")
                st.rerun()
        else:
            st.info("No doctors to remove")

# ──── Appointments ──────────────────────────────────────────────────────

elif page == "📅 Appointments":
    st.title("📅 Appointment Queue")
    tab1, tab2, tab3 = st.tabs(["➕ Book", "📋 Queue", "✅ Complete"])

    with tab1:
        patients = pm.get_all_patients()
        doctors = dm.get_all_doctors()
        with st.form("book_appointment"):
            if patients:
                patient_opts = {f"{p.get('patient_id')} - {p.get('name')}": p for p in patients}
                selected_patient = st.selectbox("Patient", list(patient_opts.keys()))
            else:
                st.warning("No patients available")
                selected_patient = None
            if doctors:
                doc_opts = {f"{d.get('doctor_id')} - {d.get('name')} ({d.get('department')})": d for d in doctors}
                selected_doc = st.selectbox("Doctor", list(doc_opts.keys()))
            else:
                st.warning("No doctors available")
                selected_doc = None
            if st.form_submit_button("📅 Book Appointment", use_container_width=True, type="primary"):
                if selected_patient and selected_doc:
                    pat = patient_opts[selected_patient]
                    doc = doc_opts[selected_doc]
                    am.book_appointment(pat["patient_id"], pat["name"], doc["name"], doc["department"])
                    st.success("✅ Appointment booked!")
                    st.rerun()
                else:
                    st.warning("⚠️ Select both patient and doctor")

    with tab2:
        queue = am.get_queue()
        if queue:
            st.dataframe(queue, use_container_width=True, hide_index=True)
            st.metric("📊 Queue Size", len(queue))
        else:
            st.info("Queue is empty")

    with tab3:
        next_a = am.next_appointment()
        if next_a:
            st.info(f"Next: {next_a.get('patient_name')} → {next_a.get('doctor_name')}")
            if st.button("✅ Complete Appointment", use_container_width=True, type="primary"):
                am.complete_appointment()
                st.success("✅ Appointment completed!")
                st.rerun()
        else:
            st.info("No appointments to complete")

# ──── Medical History ───────────────────────────────────────────────────

elif page == "📖 Medical History":
    st.title("📖 Medical History")
    patients = pm.get_all_patients()
    if not patients:
        st.info("No patients registered. Add a patient first.")
    else:
        patient_opts = {f"{p.get('patient_id')} - {p.get('name')}": p for p in patients}
        selected_label = st.selectbox("Select Patient", list(patient_opts.keys()))
        selected = patient_opts[selected_label]
        pid = selected["patient_id"]
        mh.set_current_patient(pid)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("◀ Previous Visit", use_container_width=True):
                result = mh.previous_visit(pid)
                if result:
                    st.rerun()
                else:
                    st.warning("At the oldest record")
        with c2:
            if st.button("Next Visit ▶", use_container_width=True):
                result = mh.next_visit(pid)
                if result:
                    st.rerun()
                else:
                    st.warning("At the newest record")
        with c3:
            if st.button("➕ Add Visit", use_container_width=True):
                st.session_state.show_add_visit = True
        with c4:
            count = mh.get_history_count(pid)
            pos = mh.get_current_position(pid) + 1
            st.metric("Visit", f"{pos} of {count}" if count > 0 else "0")

        current = mh.current_visit(pid)
        if current:
            st.subheader("📍 Current Visit")
            st.markdown(
                f"<div style='border:2px solid #4CAF50; border-radius:12px; padding:16px; background:#0e1117;'>"
                f"<p><strong>Doctor:</strong> {current.get('doctor_name', 'N/A')}</p>"
                f"<p><strong>Diagnosis:</strong> {current.get('diagnosis', 'N/A')}</p>"
                f"<p><strong>Prescription:</strong> {current.get('prescription', 'N/A')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if ai.is_configured():
                if st.button("💊 Explain Prescription with AI", use_container_width=True):
                    with st.spinner("Explaining prescription..."):
                        explanation = ai.explain_prescription(
                            current.get("prescription", ""),
                            current.get("diagnosis", ""),
                            current.get("doctor_name", ""),
                        )
                    if explanation:
                        st.markdown("---")
                        st.markdown(explanation)

        if st.session_state.get("show_add_visit"):
            with st.form("add_visit"):
                diagnosis = st.text_area("Diagnosis")
                prescription = st.text_area("Prescription")
                doctor_name = st.text_input("Doctor Name")
                if st.form_submit_button("💾 Save Visit", use_container_width=True, type="primary"):
                    if diagnosis and doctor_name:
                        mh.add_visit(pid, diagnosis, prescription, doctor_name)
                        st.success("✅ Visit added!")
                        st.session_state.show_add_visit = False
                        st.rerun()
                    else:
                        st.warning("Diagnosis and Doctor Name required")

        st.divider()
        st.subheader("📋 Complete Medical History")
        history = mh.get_history(pid)
        if history:
            st.dataframe(history, use_container_width=True, hide_index=True)
        else:
            st.info("No medical history for this patient")

# ──── Doctor Rotation ───────────────────────────────────────────────────

elif page == "🔄 Doctor Rotation":
    st.title("🔄 Doctor Duty Rotation")

    current = dm.current_doctor()
    if current:
        st.subheader("👨‍⚕️ Current Doctor On Duty")
        st.markdown(
            f"<div style='border:2px solid #FF9800; border-radius:12px; padding:20px; text-align:center; background:#1a1a0e;'>"
            f"<h2>⭐ {current.get('name', 'N/A')}</h2>"
            f"<p><strong>Department:</strong> {current.get('department', 'N/A')} | <strong>Shift:</strong> {current.get('shift', 'N/A')}</p>"
            f"<p><strong>ID:</strong> {current.get('doctor_id', 'N/A')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No doctors registered")

    if st.button("🔄 Rotate Duty", use_container_width=True, type="primary"):
        result = dm.rotate_duty()
        if result:
            st.success(f"✅ Duty rotated to {result.get('name')}")
            st.rerun()
        else:
            st.warning("No doctors to rotate")

    st.divider()
    st.subheader("📋 All Doctors")
    doctors = dm.get_all_doctors()
    if doctors:
        current_id = current.get("doctor_id") if current else None
        for doc in doctors:
            is_current = doc.get("doctor_id") == current_id
            border = "2px solid #FF9800" if is_current else "1px solid #333"
            bg = "#1a1a0e" if is_current else "#0e1117"
            st.markdown(
                f"<div style='border:{border}; border-radius:8px; padding:12px; margin:4px 0; background:{bg};'>"
                f"{'⭐ ' if is_current else ''}<strong>{doc.get('name', '')}</strong> — {doc.get('department', '')} ({doc.get('shift', '')})"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No doctors registered")

# ──── AI Health Assistant ───────────────────────────────────────────────

elif page == "🤖 AI Health Assistant":
    st.title("🤖 AI Health Assistant")
    st.caption("Ask health-related questions to the AI assistant. Not a substitute for professional medical advice.")

    if not ai.is_configured():
        st.warning("⚠️ Please add your Gemini API key in **Settings** to use the AI Health Assistant.")
        st.info("🔑 Go to Settings → AI Configuration → Enter your Gemini API Key")
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["content"])
            else:
                st.chat_message("assistant").markdown(msg["content"])

        user_input = st.chat_input("Type your health question here...")
        if user_input:
            st.chat_message("user").markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = ai.chat(user_input, st.session_state.chat_history)
                if response:
                    st.markdown(response)
                else:
                    st.error("Failed to get response. Check your API key.")
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})

        if st.session_state.chat_history and st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ──── Reports ───────────────────────────────────────────────────────────

elif page == "📊 Reports":
    patients = pm.get_all_patients()
    doctors = dm.get_all_doctors()
    appointments = am.get_queue()
    render_reports(patients, doctors, appointments)

# ──── Linked List Visualizer ────────────────────────────────────────────

elif page == "🔗 Linked List Viz":
    st.title("🔗 Linked List Visualizer")
    st.caption("Visual representation of all linked data structures in the system")

    viz_tabs = st.tabs(["👤 Patient SLL", "📖 Medical DLL", "👨‍⚕️ Doctor CLL", "📅 Appointment Queue"])

    with viz_tabs[0]:
        from linked_list import SinglyLinkedList
        sll = SinglyLinkedList()
        patients = pm.get_all_patients()
        sll.rebuild(patients)
        render_patient_viz(sll)
        if patients:
            st.dataframe(patients, use_container_width=True, hide_index=True)

    with viz_tabs[1]:
        patients = pm.get_all_patients()
        if patients:
            patient_opts = {f"{p.get('patient_id')} - {p.get('name')}": p for p in patients}
            sel = st.selectbox("Select Patient", list(patient_opts.keys()), key="viz_med")
            pid = patient_opts[sel]["patient_id"]
            dll = mh._get_list(pid)
            render_medical_viz(dll)
            history = dll.to_list()
            if history:
                st.dataframe(history, use_container_width=True, hide_index=True)
        else:
            st.info("No patients available")

    with viz_tabs[2]:
        render_doctor_viz(dm.list)
        doctors = dm.get_all_doctors()
        if doctors:
            st.dataframe(doctors, use_container_width=True, hide_index=True)

    with viz_tabs[3]:
        render_appointment_viz(am.queue)
        queue = am.get_queue()
        if queue:
            st.dataframe(queue, use_container_width=True, hide_index=True)

# ──── Global Search ─────────────────────────────────────────────────────

elif page == "🔍 Global Search":
    st.title("🔍 Global Search")
    st.caption("Search across patients, doctors, and appointments")
    search_engine = SearchEngine(pm, dm, am)
    query = st.text_input("Search query", placeholder="Type name, ID, department, blood group...", label_visibility="collapsed")
    if query:
        results = search_engine.search_all(query)
        total = sum(len(v) for v in results.values())
        if total == 0:
            st.warning("No results found")
        else:
            st.success(f"Found {total} result(s)")

            if results["patients"]:
                st.subheader(f"👤 Patients ({len(results['patients'])})")
                st.dataframe(results["patients"], use_container_width=True, hide_index=True)

            if results["doctors"]:
                st.subheader(f"👨‍⚕️ Doctors ({len(results['doctors'])})")
                st.dataframe(results["doctors"], use_container_width=True, hide_index=True)

            if results["appointments"]:
                st.subheader(f"📅 Appointments ({len(results['appointments'])})")
                st.dataframe(results["appointments"], use_container_width=True, hide_index=True)

# ──── Settings ──────────────────────────────────────────────────────────

elif page == "⚙ Settings":
    st.title("⚙ Settings")

    tab_s1, tab_s2 = st.tabs(["🤖 AI Configuration", "🗄️ Database & System"])

    with tab_s1:
        st.subheader("🔑 Gemini API Key Configuration")
        current_key = st.session_state.get("gemini_api_key", "")
        if current_key:
            st.success("✅ API key is configured")
            masked = current_key[:8] + "..." + current_key[-4:]
            st.code(masked)
            if st.button("🗑️ Delete API Key", use_container_width=True):
                st.session_state.gemini_api_key = ""
                st.rerun()
        else:
            st.warning("⚠️ No API key configured")
            st.info("Get a free API key from https://aistudio.google.com/app/apikey")

        api_key = st.text_input("Enter your Gemini API Key", type="password", placeholder="AIza...")
        if st.button("💾 Save & Validate Key", use_container_width=True, type="primary"):
            if api_key:
                with st.spinner("Validating..."):
                    if ai.validate_key(api_key):
                        st.session_state.gemini_api_key = api_key
                        st.success("✅ Valid API key! AI features are now active.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid API key. Please check and try again.")
            else:
                st.warning("⚠️ Please enter an API key")

        st.divider()
        st.subheader("🤖 Supported Models")
        st.code("gemini-2.5-flash (default)\ngemini-2.5-pro")
        st.caption("⚠️ **Disclaimer:** This AI assistant is for educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment.")

    with tab_s2:
        st.subheader("🗄️ Database")
        st.code("Database: hospital.db")
        c1, c2, c3 = st.columns(3)
        c1.metric("Patients in DB", db.get_table_count("patients"))
        c2.metric("Doctors in DB", db.get_table_count("doctors"))
        c3.metric("Appointments in DB", db.get_table_count("appointments"))

        st.divider()
        st.subheader("📋 System Info")
        st.code("Linked List: Patient SLL (Singly), Medical DLL (Doubly), Doctor CLL (Circular), Appointment Queue")

        if st.button("🔄 Reload All Data from Database", use_container_width=True):
            for key in ["pm", "dm", "am", "mh"]:
                st.session_state[key] = None
            st.rerun()
