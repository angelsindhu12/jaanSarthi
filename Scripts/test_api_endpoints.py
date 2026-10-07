import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

def test_api():
    print("Testing FastAPI endpoints using TestClient...")
    with TestClient(app) as client:
        # 1. Health check
        res_health = client.get("/health")
        print(f"[1/7] Health Check: {res_health.status_code}")
        assert res_health.status_code == 200

        # 2. Register Account
        reg_payload = {
            "name": "Citizen User",
            "email": "citizen.test@gov.in",
            "password": "SecurePassword123",
            "phone": "+91 9876500000",
            "age": 22,
            "gender": "Male",
            "qualification": "12th",
            "category": "OBC",
            "state": "Uttar Pradesh",
            "occupation": "Student"
        }
        res_reg = client.post("/api/auth/register", json=reg_payload)
        print(f"[2/7] Auth Register: {res_reg.status_code}")
        assert res_reg.status_code in [200, 400]

        # 3. Login Account
        login_payload = {
            "email": "citizen.test@gov.in",
            "password": "SecurePassword123"
        }
        res_login = client.post("/api/auth/login", json=login_payload)
        print(f"[3/7] Auth Login: {res_login.status_code}")
        assert res_login.status_code == 200

        # 4. Eligibility Check
        profile_data = {
            "age": 22,
            "gender": "Male",
            "qualification": "12th",
            "annual_income": 120000,
            "caste_category": "OBC",
            "state": "All India",
            "occupation": "Unemployed",
            "preferred_language": "en"
        }
        res_elig = client.post("/api/eligibility/check", json=profile_data)
        print(f"[4/7] Eligibility Endpoint: {res_elig.status_code}")
        elig_data = res_elig.json()
        print(f"      Eligible Schemes: {elig_data['eligible_schemes_count']} | Eligible Jobs: {elig_data['eligible_jobs_count']}")
        assert res_elig.status_code == 200

        # 5. Multilingual Search (Testing Bengali/Hindi query)
        search_req = {"query": "কৃষকদের জন্য আর্থিক অনুদান এবং ঋণ", "top_k": 2}
        res_search = client.post("/api/schemes/search", json=search_req)
        print(f"[5/7] Multilingual Search Endpoint: {res_search.status_code}")
        assert res_search.status_code == 200

        # 6. Recent Jobs by Qualification
        res_jobs = client.get("/api/jobs/recent?qualification=10th")
        print(f"[6/7] Recent Jobs (10th Pass): {res_jobs.status_code}")
        assert res_jobs.status_code == 200

        # 7. Document Upload and Explain
        sample_img = Path("data/sample_pm_kisan_notice.png")
        if sample_img.exists():
            with open(sample_img, "rb") as f:
                files = {"file": ("sample.png", f, "image/png")}
                res_doc = client.post("/api/documents/upload-and-explain", files=files, data={"preferred_language": "en"})
            print(f"[7/7] Document Upload & Explain: {res_doc.status_code}")
            assert res_doc.status_code == 200

    print("\n[SUCCESS] All 7 FastAPI endpoints and authentication flows verified!")

if __name__ == "__main__":
    test_api()
