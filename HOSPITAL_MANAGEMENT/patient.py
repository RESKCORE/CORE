from __future__ import annotations
from typing import Optional, List
from linked_list import SinglyLinkedList
from database import DatabaseManager
from utils import generate_id


class PatientManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.list = SinglyLinkedList()
        self._load()

    def _load(self) -> None:
        patients = self.db.load_patients()
        self.list.rebuild(patients)

    def _save(self) -> None:
        self.db.save_patients(self.list.to_list())

    def add_patient(self, name: str, age: int, gender: str, contact: str, blood_group: str) -> Optional[dict]:
        existing_ids = [p.get("patient_id", "") for p in self.list.to_list()]
        patient_id = generate_id("PAT", existing_ids)
        data = {
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "gender": gender,
            "contact": contact,
            "blood_group": blood_group,
        }
        self.list.insert_at_end(data)
        self._save()
        return data

    def delete_patient(self, patient_id: str) -> bool:
        result = self.list.delete("patient_id", patient_id)
        if result:
            self._save()
        return result

    def update_patient(self, patient_id: str, **kwargs) -> bool:
        result = self.list.update("patient_id", patient_id, kwargs)
        if result:
            self._save()
        return result

    def search_patient(self, patient_id: str) -> Optional[dict]:
        return self.list.search("patient_id", patient_id)

    def search_by_name(self, name: str) -> List[dict]:
        return self.list.search_multi("name", name)

    def get_all_patients(self) -> List[dict]:
        return self.list.to_list()

    @property
    def count(self) -> int:
        return self.list.size

    def get_patient_ids(self) -> List[str]:
        return [p.get("patient_id", "") for p in self.list.to_list()]

    def get_patient_names(self) -> dict:
        return {p.get("patient_id"): p.get("name", "") for p in self.list.to_list()}
