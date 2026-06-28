from __future__ import annotations
from typing import Optional, List
from linked_list import DoublyLinkedList
from database import DatabaseManager
from datetime import datetime


class MedicalHistoryManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.histories: dict[str, DoublyLinkedList] = {}
        self._current_patient_id: Optional[str] = None

    def _get_list(self, patient_id: str) -> DoublyLinkedList:
        if patient_id not in self.histories:
            self.histories[patient_id] = DoublyLinkedList()
            records = self.db.load_medical_history(patient_id)
            self.histories[patient_id].rebuild(records, len(records) - 1)
        return self.histories[patient_id]

    def _save(self, patient_id: str) -> None:
        records = self.histories[patient_id].to_list()
        self.db.save_medical_history(patient_id, records)

    def set_current_patient(self, patient_id: str) -> None:
        self._current_patient_id = patient_id

    def add_visit(self, patient_id: str, diagnosis: str, prescription: str, doctor_name: str) -> Optional[dict]:
        dll = self._get_list(patient_id)
        data = {
            "visit_date": datetime.now().isoformat(),
            "diagnosis": diagnosis,
            "prescription": prescription,
            "doctor_name": doctor_name,
        }
        dll.insert(data)
        self._save(patient_id)
        return data

    def delete_visit(self, patient_id: str, visit_date: str) -> bool:
        dll = self._get_list(patient_id)
        result = dll.delete("visit_date", visit_date)
        if result:
            self._save(patient_id)
        return result

    def previous_visit(self, patient_id: str) -> Optional[dict]:
        dll = self._get_list(patient_id)
        return dll.previous()

    def next_visit(self, patient_id: str) -> Optional[dict]:
        dll = self._get_list(patient_id)
        return dll.next_visit()

    def current_visit(self, patient_id: str) -> Optional[dict]:
        dll = self._get_list(patient_id)
        return dll.current_data()

    def get_history(self, patient_id: str) -> List[dict]:
        dll = self._get_list(patient_id)
        return dll.to_list()

    def get_current_position(self, patient_id: str) -> int:
        dll = self._get_list(patient_id)
        return dll.current_position()

    def get_history_count(self, patient_id: str) -> int:
        dll = self._get_list(patient_id)
        return dll.size
