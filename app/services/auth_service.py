import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

import re

USERS_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "users_db.json"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class AuthService:
    @staticmethod
    def _load_db() -> Dict[str, Any]:
        if not USERS_DB_PATH.exists():
            USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}
        try:
            with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_db(db: Dict[str, Any]):
        USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    @classmethod
    def register(cls, name: str, email: str, password: str, phone: str = "", age: int = 21,
                 gender: str = "Male", qualification: str = "12th", category: str = "General",
                 state: str = "All India", occupation: str = "Student") -> Dict[str, Any]:
        email = email.strip().lower()
        if not email or not password:
            return {"success": False, "message": "Email and password are required."}

        if not re.match(EMAIL_REGEX, email):
            return {"success": False, "message": "Please enter a valid email address (e.g. citizen@gmail.com)."}

        db = cls._load_db()
        if email in db:
            return {"success": False, "message": "User with this email already exists. Please login."}

        user_data = {
            "name": name.strip(),
            "email": email,
            "password_hash": hash_password(password),
            "phone": phone.strip(),
            "profile": {
                "full_name": name.strip(),
                "age": age,
                "gender": gender,
                "qualification": qualification,
                "annual_income": 150000,
                "caste_category": category,
                "state": state,
                "occupation": occupation,
                "phone": phone.strip(),
                "email": email
            },
            "applications_filled": [],
            "past_exams": [],
            "settings": {
                "daily_job_alerts": True,
                "daily_scheme_alerts": True,
                "sms_notifications": False,
                "notification_frequency": "Daily",
                "preferred_language": "en"
            }
        }
        db[email] = user_data
        cls._save_db(db)
        return {"success": True, "message": "Registration successful! You can now login.", "user": user_data}

    @classmethod
    def login(cls, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()
        if not email or not password:
            return {"success": False, "message": "Email and password are required."}
        if not re.match(EMAIL_REGEX, email):
            return {"success": False, "message": "Please enter a valid email address (e.g. citizen@gmail.com)."}
        db = cls._load_db()
        if email not in db:
            return {"success": False, "message": "No account found with this email. Please register."}

        user = db[email]
        if user["password_hash"] != hash_password(password):
            return {"success": False, "message": "Invalid password. Please try again."}

        return {"success": True, "message": "Login successful!", "user": user}

    @classmethod
    def get_user(cls, email: str) -> Optional[Dict[str, Any]]:
        email = email.strip().lower()
        db = cls._load_db()
        return db.get(email)

    @classmethod
    def update_profile(cls, email: str, profile_data: Dict[str, Any]) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            db[email]["profile"] = profile_data
            cls._save_db(db)
            return True
        return False

    @classmethod
    def update_settings(cls, email: str, settings_data: Dict[str, Any]) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            db[email]["settings"] = settings_data
            cls._save_db(db)
            return True
        return False

    @classmethod
    def add_application(cls, email: str, app_entry: Dict[str, Any]) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            db[email].setdefault("applications_filled", []).insert(0, app_entry)
            cls._save_db(db)
            return True
        return False

    @classmethod
    def add_exam(cls, email: str, exam_entry: Dict[str, Any]) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            db[email].setdefault("past_exams", []).insert(0, exam_entry)
            cls._save_db(db)
            return True
        return False

    @classmethod
    def delete_application(cls, email: str, index: int) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            apps = db[email].get("applications_filled", [])
            if 0 <= index < len(apps):
                apps.pop(index)
                cls._save_db(db)
                return True
        return False

    @classmethod
    def delete_exam(cls, email: str, index: int) -> bool:
        email = email.strip().lower()
        db = cls._load_db()
        if email in db:
            exams = db[email].get("past_exams", [])
            if 0 <= index < len(exams):
                exams.pop(index)
                cls._save_db(db)
                return True
        return False
