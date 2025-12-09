from __future__ import annotations
from typing import Dict, Any
from datetime import date


class MemberFactory:
    @staticmethod
    def create_student(
        student_id: int,
        full_name: str,
        email: str,
        phone: str,
        address: str,
        join_date: str,
        subscription_status: str = "Pending",
        groupe: int | None = None,
        skills: list[str] | None = None,
        interests: list[str] | None = None,
    ) -> Dict[str, Any]:
        return {
            "student_id": student_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "join_date": join_date,
            "groupe": groupe,
            "subscription_status": subscription_status,
            "skills": skills or [],
            "interests": interests or [],
        }

    @staticmethod
    def create_teacher(
        teacher_id: int,
        full_name: str,
        email: str,
        phone: str,
        address: str,
        join_date: str,
        skills: list[str] | None = None,
        interests: list[str] | None = None,
    ) -> Dict[str, Any]:
        return {
            "teacher_id": teacher_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "join_date": join_date,
            "skills": skills or [],
            "interests": interests or [],
        }

