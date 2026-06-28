from __future__ import annotations
import sqlite3
import os
from typing import Optional, List, Any
from datetime import datetime


DB_NAME = "hospital.db"


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _create_tables(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    contact TEXT,
                    blood_group TEXT
                );

                CREATE TABLE IF NOT EXISTS medical_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    visit_date TEXT,
                    diagnosis TEXT,
                    prescription TEXT,
                    doctor_name TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                );

                CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT,
                    shift TEXT
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    patient_name TEXT,
                    doctor_name TEXT,
                    department TEXT,
                    appointment_date TEXT,
                    status TEXT DEFAULT 'waiting',
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                );
            """)

    # ── Patients ────────────────────────────────────────────────────────

    def load_patients(self) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM patients ORDER BY rowid").fetchall()
            return [dict(r) for r in rows]

    def save_patients(self, patients: List[dict]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM patients")
            for p in patients:
                conn.execute(
                    "INSERT INTO patients (patient_id, name, age, gender, contact, blood_group) VALUES (?, ?, ?, ?, ?, ?)",
                    (p.get("patient_id"), p.get("name"), p.get("age"), p.get("gender"), p.get("contact"), p.get("blood_group")),
                )
            conn.commit()

    # ── Medical History ─────────────────────────────────────────────────

    def load_medical_history(self, patient_id: str) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM medical_history WHERE patient_id = ? ORDER BY rowid", (patient_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def save_medical_history(self, patient_id: str, records: List[dict]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM medical_history WHERE patient_id = ?", (patient_id,))
            for r in records:
                conn.execute(
                    "INSERT INTO medical_history (patient_id, visit_date, diagnosis, prescription, doctor_name) VALUES (?, ?, ?, ?, ?)",
                    (patient_id, r.get("visit_date"), r.get("diagnosis"), r.get("prescription"), r.get("doctor_name")),
                )
            conn.commit()

    # ── Doctors ─────────────────────────────────────────────────────────

    def load_doctors(self) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM doctors ORDER BY rowid").fetchall()
            return [dict(r) for r in rows]

    def save_doctors(self, doctors: List[dict]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM doctors")
            for d in doctors:
                conn.execute(
                    "INSERT INTO doctors (doctor_id, name, department, shift) VALUES (?, ?, ?, ?)",
                    (d.get("doctor_id"), d.get("name"), d.get("department"), d.get("shift")),
                )
            conn.commit()

    # ── Appointments ────────────────────────────────────────────────────

    def load_appointments(self) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM appointments ORDER BY rowid").fetchall()
            return [dict(r) for r in rows]

    def save_appointments(self, appointments: List[dict]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM appointments")
            for a in appointments:
                conn.execute(
                    "INSERT INTO appointments (patient_id, patient_name, doctor_name, department, appointment_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (a.get("patient_id"), a.get("patient_name"), a.get("doctor_name"), a.get("department"), a.get("appointment_date"), a.get("status", "waiting")),
                )
            conn.commit()

    # ── Utility ─────────────────────────────────────────────────────────

    def get_table_count(self, table: str) -> int:
        with self._connect() as conn:
            row = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}").fetchone()
            return row["cnt"] if row else 0
