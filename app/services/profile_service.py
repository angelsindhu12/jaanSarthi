import json
from pathlib import Path
from typing import Dict, Any, List

PROFILE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "user_profile.json"

DEFAULT_PROFILE = {
    "personal_info": {
        "full_name": "",
        "age": 21,
        "gender": "Male",
        "qualification": "12th",
        "annual_income": 150000,
        "caste_category": "General",
        "state": "All India",
        "occupation": "Student",
        "phone": "",
        "email": ""
    },
    "education_records": [],
    "applications_filled": [],
    "past_exams": []
}

class ProfileManager:
    @staticmethod
    def get_profile() -> Dict[str, Any]:
        if not PROFILE_PATH.exists():
            PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_PROFILE, f, ensure_ascii=False, indent=2)
            return DEFAULT_PROFILE

        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure no bookmarks present
                if "bookmarked_schemes" in data:
                    del data["bookmarked_schemes"]
                return data
        except Exception:
            return DEFAULT_PROFILE

    @staticmethod
    def save_profile(profile_data: Dict[str, Any]):
        PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Ensure no bookmarks
        if "bookmarked_schemes" in profile_data:
            del profile_data["bookmarked_schemes"]
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_application(app_entry: Dict[str, Any]):
        profile = ProfileManager.get_profile()
        profile.setdefault("applications_filled", []).insert(0, app_entry)
        ProfileManager.save_profile(profile)

    @staticmethod
    def add_exam(exam_entry: Dict[str, Any]):
        profile = ProfileManager.get_profile()
        profile.setdefault("past_exams", []).insert(0, exam_entry)
        ProfileManager.save_profile(profile)

    @staticmethod
    def delete_application(index: int):
        profile = ProfileManager.get_profile()
        apps = profile.get("applications_filled", [])
        if 0 <= index < len(apps):
            apps.pop(index)
            ProfileManager.save_profile(profile)

    @staticmethod
    def delete_exam(index: int):
        profile = ProfileManager.get_profile()
        exams = profile.get("past_exams", [])
        if 0 <= index < len(exams):
            exams.pop(index)
            ProfileManager.save_profile(profile)
