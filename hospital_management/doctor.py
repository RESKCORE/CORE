from __future__ import annotations
from typing import Optional, List
from linked_list import CircularLinkedList
from database import DatabaseManager
from utils import generate_id


class DoctorManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.list = CircularLinkedList()
        self._load()

    def _load(self) -> None:
        doctors = self.db.load_doctors()
        self.list.rebuild(doctors)

    def _save(self) -> None:
        self.db.save_doctors(self.list.to_list())

    def add_doctor(self, name: str, department: str, shift: str) -> Optional[dict]:
        existing_ids = [d.get("doctor_id", "") for d in self.list.to_list()]
        doctor_id = generate_id("DOC", existing_ids)
        data = {
            "doctor_id": doctor_id,
            "name": name,
            "department": department,
            "shift": shift,
        }
        self.list.insert(data)
        self._save()
        return data

    def remove_doctor(self, doctor_id: str) -> bool:
        result = self.list.remove("doctor_id", doctor_id)
        if result:
            self._save()
        return result

    def rotate_duty(self) -> Optional[dict]:
        result = self.list.rotate()
        if result:
            self._save()
        return result

    def current_doctor(self) -> Optional[dict]:
        return self.list.current_data()

    def get_all_doctors(self) -> List[dict]:
        return self.list.to_list()

    @property
    def count(self) -> int:
        return self.list.size
