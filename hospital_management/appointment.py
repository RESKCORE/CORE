from __future__ import annotations
from typing import Optional, List
from linked_list import Queue
from database import DatabaseManager
from datetime import datetime


class AppointmentManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.queue = Queue()
        self._load()

    def _load(self) -> None:
        appointments = self.db.load_appointments()
        self.queue.rebuild(appointments)

    def _save(self) -> None:
        self.db.save_appointments(self.queue.to_list())

    def book_appointment(self, patient_id: str, patient_name: str, doctor_name: str, department: str, date: Optional[str] = None) -> Optional[dict]:
        data = {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "department": department,
            "appointment_date": date or datetime.now().isoformat(),
            "status": "waiting",
        }
        self.queue.enqueue(data)
        self._save()
        return data

    def cancel_appointment(self, patient_id: str) -> bool:
        result = self.queue.remove("patient_id", patient_id)
        if result:
            self._save()
        return result

    def complete_appointment(self) -> Optional[dict]:
        data = self.queue.dequeue()
        if data:
            data["status"] = "completed"
            self._save()
        return data

    def get_queue(self) -> List[dict]:
        return self.queue.to_list()

    def next_appointment(self) -> Optional[dict]:
        return self.queue.peek()

    @property
    def count(self) -> int:
        return self.queue.size
