import json
import torch
from pathlib import Path
from typing import List, Dict, Any
from app.core.schemas import UserProfileInput
from app.ml.data_loader import DatasetLoader
from app.ml.train_eligibility_model import EligibilityNeuralNet, extract_feature_vector, QUALIFICATION_MAP

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

class EligibilityMatcher:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = EligibilityNeuralNet(input_dim=16).to(self.device)
        model_path = MODELS_DIR / "eligibility_classifier.pt"
        
        if model_path.exists():
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            self.model.eval()
            print(f"[Matcher] Loaded trained Neural Network from {model_path} on {self.device}")
        else:
            print("[Matcher] Warning: Model file not found, using untransformed baseline.")

        self.schemes = DatasetLoader.load_schemes()
        self.jobs = DatasetLoader.load_jobs()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate_schemes(self, user_dict: dict, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        results = []
        user_qual_val = QUALIFICATION_MAP.get(user_dict.get("qualification", "12th"), 3)
        user_age = user_dict.get("age", 25)
        user_gender = user_dict.get("gender", "All")
        user_income = user_dict.get("annual_income") or 150000
        user_cat = user_dict.get("caste_category", "General")
        user_occ = user_dict.get("occupation", "Any")
        lang = user_dict.get("preferred_language", "hi")

        for scheme in self.schemes:
            feat = extract_feature_vector(user_dict, scheme, is_job=False)
            with torch.no_grad():
                tensor_feat = torch.tensor([feat], dtype=torch.float32).to(self.device)
                prob = self.model(tensor_feat).item()

            elig = scheme.get("eligibility", {})
            reasons_en = []
            reasons_hi = []

            # Determine eligibility reasons
            if user_age < elig["min_age"] or user_age > elig["max_age"]:
                reasons_en.append(f"Age must be between {elig['min_age']} and {elig['max_age']}.")
                reasons_hi.append(f"आयु {elig['min_age']} से {elig['max_age']} वर्ष के बीच होनी चाहिए।")
            
            if elig["gender"] != "All" and user_gender != elig["gender"]:
                reasons_en.append(f"Only open for {elig['gender']} beneficiaries.")
                reasons_hi.append(f"यह केवल {elig['gender']} लाभार्थियों के लिए है।")

            if elig["max_annual_income"] and user_income > elig["max_annual_income"]:
                reasons_en.append(f"Annual income exceeds limit of Rs {elig['max_annual_income']:,}.")
                reasons_hi.append(f"वार्षिक आय ₹{elig['max_annual_income']:,} की सीमा से अधिक है।")

            if "All" not in elig.get("caste_category", ["All"]) and user_cat not in elig.get("caste_category", []):
                reasons_en.append(f"Eligible categories: {', '.join(elig['caste_category'])}.")
                reasons_hi.append(f"पात्र श्रेणियां: {', '.join(elig['caste_category'])}।")

            is_eligible = (prob >= min_confidence) and (len(reasons_en) == 0)

            results.append({
                "scheme_id": scheme["id"],
                "title_en": scheme["title_en"],
                "title_hi": scheme["title_hi"],
                "category": scheme["category"],
                "is_eligible": is_eligible,
                "confidence_score": round(prob, 4),
                "summary": scheme["summary_hi"] if lang == "hi" else scheme["summary_en"],
                "benefits": scheme["benefits_hi"] if lang == "hi" else scheme["benefits_en"],
                "documents_required": scheme.get("documents_required", []),
                "application_url": scheme["application_url"],
                "status_message": (
                    "आप इस योजना के लिए पूरी तरह पात्र हैं।" if is_eligible else f"अपात्रता कारण: {' '.join(reasons_hi)}"
                ) if lang == "hi" else (
                    "You are eligible for this scheme!" if is_eligible else f"Ineligible: {' '.join(reasons_en)}"
                )
            })

        # Sort: eligible first, then by confidence score descending
        results.sort(key=lambda x: (x["is_eligible"], x["confidence_score"]), reverse=True)
        return results

    def evaluate_jobs(self, user_dict: dict, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        results = []
        user_qual_val = QUALIFICATION_MAP.get(user_dict.get("qualification", "12th"), 3)
        user_age = user_dict.get("age", 25)
        lang = user_dict.get("preferred_language", "hi")

        for job in self.jobs:
            feat = extract_feature_vector(user_dict, job, is_job=True)
            with torch.no_grad():
                tensor_feat = torch.tensor([feat], dtype=torch.float32).to(self.device)
                prob = self.model(tensor_feat).item()

            job_req_qual_val = QUALIFICATION_MAP.get(job["qualification_required"], 2)
            qual_ok = user_qual_val >= job_req_qual_val
            age_ok = job["min_age"] <= user_age <= job["max_age"]
            is_eligible = qual_ok and age_ok and (prob >= min_confidence)

            reasons_en = []
            reasons_hi = []
            if not qual_ok:
                reasons_en.append(f"Requires minimum qualification: {job['qualification_required']}.")
                reasons_hi.append(f"न्यूनतम शैक्षणिक योग्यता {job['qualification_required']} आवश्यक है।")
            if not age_ok:
                reasons_en.append(f"Age must be between {job['min_age']} and {job['max_age']}.")
                reasons_hi.append(f"आयु सीमा {job['min_age']} से {job['max_age']} वर्ष होनी चाहिए।")

            results.append({
                "job_id": job["job_id"],
                "title_en": job["title_en"],
                "title_hi": job["title_hi"],
                "organization": job["organization"],
                "qualification_required": job["qualification_required"],
                "vacancies": job["vacancies"],
                "application_deadline": job["application_deadline"],
                "official_portal": job["official_portal"],
                "is_eligible": is_eligible,
                "confidence_score": round(prob, 4),
                "summary": job["summary_hi"] if lang == "hi" else job["summary_en"],
                "status_message": (
                    f"आपकी योग्यता ({user_dict.get('qualification')}) इस भर्ती के अनुकूल है। आप {job['official_portal']} पर सीधे आवेदन कर सकते हैं।" if is_eligible else f"अपात्रता: {' '.join(reasons_hi)}"
                ) if lang == "hi" else (
                    f"Your qualification matches! You can apply directly at {job['official_portal']}." if is_eligible else f"Ineligible: {' '.join(reasons_en)}"
                )
            })

        # Sort: eligible first, then by confidence score
        results.sort(key=lambda x: (x["is_eligible"], x["confidence_score"]), reverse=True)
        return results

    def match_all(self, profile: UserProfileInput) -> Dict[str, Any]:
        user_dict = profile.model_dump()
        schemes = self.evaluate_schemes(user_dict)
        jobs = self.evaluate_jobs(user_dict)

        eligible_schemes = [s for s in schemes if s["is_eligible"]]
        eligible_jobs = [j for j in jobs if j["is_eligible"]]

        return {
            "user_profile": user_dict,
            "total_schemes_checked": len(schemes),
            "eligible_schemes_count": len(eligible_schemes),
            "eligible_schemes": eligible_schemes,
            "other_schemes": [s for s in schemes if not s["is_eligible"]],
            "total_jobs_checked": len(jobs),
            "eligible_jobs_count": len(eligible_jobs),
            "eligible_jobs": eligible_jobs,
            "other_jobs": [j for j in jobs if not j["is_eligible"]]
        }
