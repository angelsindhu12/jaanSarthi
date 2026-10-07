import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.ml.rag_engine import MultilingualRAGEngine

def main():
    rag = MultilingualRAGEngine.get_instance()
    print("[1/3] Indexing schemes and jobs into ChromaDB...")
    rag.index_all(force_reload=False)

    print("\n[2/3] Testing Multilingual Search for Schemes...")
    test_scheme_queries = [
        "गरीब किसानों को 6000 रुपये मिलने वाली योजना",  # Hindi: Farmer Rs 6000 scheme
        "How to get free hospital treatment up to 5 lakh rupees?", # English: Healthcare / Ayushman
        "कारीगरों और बढ़ई के लिए टूलकिट और 5% पर लोन"  # Hindi: Vishwakarma artisan scheme
    ]

    for q in test_scheme_queries:
        print(f"\n>> Query: '{q}'")
        results = rag.search_schemes(q, top_k=2)
        for r in results:
            print(f"   [Match: {r['title_en']}] | Similarity: {r['similarity_score']}")
            print(f"   Hindi Title: {r['title_hi']}")
            print(f"   Benefits (EN): {r['benefits_en']}")

    print("\n[3/3] Testing Multilingual Search for Job Notifications...")
    test_job_queries = [
        "10वीं पास के लिए कौन सी नई सरकारी भर्तियां निकली हैं?", # Hindi: 10th pass jobs
        "I am a graduate looking for government bank officer jobs", # English: Bank PO
        "12th pass government clerical jobs with typing" # English: SSC CHSL
    ]

    for q in test_job_queries:
        print(f"\n>> Query: '{q}'")
        results = rag.search_jobs(q, top_k=2)
        for r in results:
            print(f"   [Match: {r['title_en']}] | Similarity: {r['similarity_score']}")
            print(f"   Required Qualification: {r['qualification_required']} | Vacancies: {r['vacancies']}")
            print(f"   Official Portal: {r['official_portal']}")

if __name__ == "__main__":
    main()
