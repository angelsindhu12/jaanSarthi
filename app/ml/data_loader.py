import json
from pathlib import Path
from typing import List, Dict, Any
from app.core.schemas import SchemeRecord, JobNotificationRecord

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

class DatasetLoader:
    _schemes: List[Dict[str, Any]] = []
    _jobs: List[Dict[str, Any]] = []
    _indic_corpus: List[Dict[str, Any]] = []

    @classmethod
    def load_schemes(cls, reload: bool = False) -> List[Dict[str, Any]]:
        if not cls._schemes or reload:
            file_path = DATA_DIR / "schemes_processed.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    cls._schemes = json.load(f)
        return cls._schemes

    @classmethod
    def load_jobs(cls, reload: bool = False) -> List[Dict[str, Any]]:
        if not cls._jobs or reload:
            file_path = DATA_DIR / "jobs_processed.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    cls._jobs = json.load(f)
        return cls._jobs

    @classmethod
    def load_indic_corpus(cls, reload: bool = False) -> List[Dict[str, Any]]:
        if not cls._indic_corpus or reload:
            file_path = DATA_DIR / "indic_corpus.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    cls._indic_corpus = json.load(f)
        return cls._indic_corpus

if __name__ == "__main__":
    schemes = DatasetLoader.load_schemes()
    jobs = DatasetLoader.load_jobs()
    print(f"Loaded {len(schemes)} schemes and {len(jobs)} jobs successfully into loader.")
