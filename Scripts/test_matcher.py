import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.schemas import UserProfileInput
from app.ml.matcher import EligibilityMatcher

def test():
    matcher = EligibilityMatcher.get_instance()

    print("\n--- Test Profile 1: 12th Pass, 20 Years Old, OBC ---")
    p1 = UserProfileInput(
        age=20,
        gender="Male",
        qualification="12th",
        annual_income=180000,
        caste_category="OBC",
        occupation="Student",
        preferred_language="hi"
    )
    res1 = matcher.match_all(p1)
    print(f"Eligible Schemes: {res1['eligible_schemes_count']}")
    for s in res1['eligible_schemes'][:2]:
        print(f"  * {s['title_hi']} (Score: {s['confidence_score']}) -> {s['status_message']}")

    print(f"Eligible Jobs: {res1['eligible_jobs_count']}")
    for j in res1['eligible_jobs'][:3]:
        print(f"  * {j['title_hi']} | Vacancies: {j['vacancies']} | Apply: {j['official_portal']}")

    print("\n--- Test Profile 2: Graduate, 24 Years Old, General ---")
    p2 = UserProfileInput(
        age=24,
        gender="Female",
        qualification="Graduate",
        annual_income=300000,
        caste_category="General",
        occupation="Unemployed",
        preferred_language="en"
    )
    res2 = matcher.match_all(p2)
    print(f"Eligible Schemes: {res2['eligible_schemes_count']}")
    print(f"Eligible Jobs: {res2['eligible_jobs_count']}")
    for j in res2['eligible_jobs'][:3]:
        print(f"  * {j['title_en']} | Required: {j['qualification_required']} | Portal: {j['official_portal']}")

if __name__ == "__main__":
    test()
