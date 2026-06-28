from __future__ import annotations
from typing import List, Dict
from patient import PatientManager
from doctor import DoctorManager
from appointment import AppointmentManager


class SearchEngine:
    def __init__(self, pm: PatientManager, dm: DoctorManager, am: AppointmentManager) -> None:
        self.pm = pm
        self.dm = dm
        self.am = am

    def search_all(self, query: str) -> Dict[str, List[dict]]:
        q = query.lower().strip()
        results: Dict[str, List[dict]] = {
            "patients": [],
            "doctors": [],
            "appointments": [],
        }
        if not q:
            return results

        for p in self.pm.get_all_patients():
            if (q in str(p.get("name", "")).lower()
                    or q in str(p.get("patient_id", "")).lower()
                    or q in str(p.get("blood_group", "")).lower()
                    or q in str(p.get("contact", ""))):
                results["patients"].append(p)

        for d in self.dm.get_all_doctors():
            if (q in str(d.get("name", "")).lower()
                    or q in str(d.get("doctor_id", "")).lower()
                    or q in str(d.get("department", "")).lower()
                    or q in str(d.get("shift", "")).lower()):
                results["doctors"].append(d)

        for a in self.am.get_queue():
            if (q in str(a.get("patient_name", "")).lower()
                    or q in str(a.get("doctor_name", "")).lower()
                    or q in str(a.get("department", "")).lower()
                    or q in str(a.get("patient_id", "")).lower()):
                results["appointments"].append(a)

        return results
