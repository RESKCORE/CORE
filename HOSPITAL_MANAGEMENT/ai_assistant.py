from __future__ import annotations
from typing import Optional, List
import streamlit as st

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


SYSTEM_PROMPT = """You are an AI Health Assistant for a Hospital Management System.
Provide helpful, accurate health information based on the user's query.
Always include this disclaimer when giving medical information:
"This information is for educational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment."
Keep responses concise, clear, and well-structured using markdown."""

PATIENT_SUMMARY_PROMPT = """Summarize the following patient information in simple, clear language.
Include key observations, risk factors, and a brief overview of their medical history.
Use markdown formatting."""

PRESCRIPTION_EXPLAIN_PROMPT = """Explain the following prescription in simple, easy-to-understand language.
Include: purpose of the medicine, how to use it, possible side effects, and precautions.
Use markdown formatting. End with the medical disclaimer."""

INSIGHTS_PROMPT = """Analyze the following hospital data and generate natural-language insights.
Highlight trends, observations, and notable patterns.
Keep it brief and use markdown bullet points."""


class AIAssistant:
    def __init__(self) -> None:
        self.model_name: str = "gemini-2.0-flash"

    def _get_client(self):
        api_key = st.session_state.get("gemini_api_key", "")
        if not api_key or not HAS_GENAI:
            return None
        return genai.Client(api_key=api_key)

    def is_configured(self) -> bool:
        return bool(st.session_state.get("gemini_api_key", "")) and HAS_GENAI

    def chat(self, message: str, history: Optional[List[dict]] = None) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None
        try:
            chat = client.chats.create(model=self.model_name, history=history or [])
            response = chat.send_message(message=f"{SYSTEM_PROMPT}\n\nUser: {message}")
            return response.text
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def generate_patient_summary(self, patient: dict, visits: List[dict]) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None
        try:
            data = f"Patient: {patient}\n\nMedical History: {visits}"
            prompt = f"{PATIENT_SUMMARY_PROMPT}\n\n{data}"
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def explain_prescription(self, prescription: str, diagnosis: str, doctor: str) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None
        try:
            data = f"Prescription: {prescription}\nDiagnosis: {diagnosis}\nDoctor: {doctor}"
            prompt = f"{PRESCRIPTION_EXPLAIN_PROMPT}\n\n{data}"
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def generate_insights(self, patients: List[dict], doctors: List[dict], appointments: List[dict]) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None
        try:
            from collections import Counter
            insights_data = {
                "total_patients": len(patients),
                "total_doctors": len(doctors),
                "total_appointments": len(appointments),
                "departments": dict(Counter(d.get("department", "Unknown") for d in doctors)),
                "blood_groups": dict(Counter(p.get("blood_group", "Unknown") for p in patients)),
                "age_range": self._age_distribution(patients),
            }
            prompt = f"{INSIGHTS_PROMPT}\n\nData: {insights_data}"
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    @staticmethod
    def _age_distribution(patients: List[dict]) -> dict:
        bins = {"0-18": 0, "19-35": 0, "36-50": 0, "51-70": 0, "70+": 0}
        for p in patients:
            try:
                a = int(p.get("age", 0) or 0)
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
        return bins

    def validate_key(self, api_key: str) -> bool:
        try:
            client = genai.Client(api_key=api_key)
            client.models.generate_content(model=self.model_name, contents="Hello")
            return True
        except Exception:
            return False
