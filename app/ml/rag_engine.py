import os
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.ml.data_loader import DatasetLoader

CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "vector_store" / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class MultilingualRAGEngine:
    _instance = None

    def __init__(self):
        # Choose GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[RAGEngine] Initializing embedding model '{MODEL_NAME}' on {self.device}...")
        self.embedder = SentenceTransformer(MODEL_NAME, device=self.device)
        
        # Initialize persistent ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.schemes_collection = self.chroma_client.get_or_create_collection(
            name="government_schemes",
            metadata={"hnsw:space": "cosine"}
        )
        self.jobs_collection = self.chroma_client.get_or_create_collection(
            name="government_jobs",
            metadata={"hnsw:space": "cosine"}
        )
        print("[RAGEngine] ChromaDB collections ready.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def index_all(self, force_reload: bool = False):
        """Embeds and indexes all processed schemes and jobs into ChromaDB."""
        # Index Schemes
        schemes = DatasetLoader.load_schemes(reload=force_reload)
        existing_schemes_count = self.schemes_collection.count()
        if existing_schemes_count == 0 or force_reload:
            print(f"[RAGEngine] Indexing {len(schemes)} schemes into vector DB...")
            if existing_schemes_count > 0:
                self.chroma_client.delete_collection("government_schemes")
                self.schemes_collection = self.chroma_client.get_or_create_collection(
                    name="government_schemes",
                    metadata={"hnsw:space": "cosine"}
                )

            ids = [s["id"] for s in schemes]
            documents = [s["search_text"] for s in schemes]
            metadatas = [
                {
                    "title_en": s["title_en"],
                    "title_hi": s["title_hi"],
                    "category": s["category"],
                    "min_age": s["eligibility"]["min_age"],
                    "max_age": s["eligibility"]["max_age"],
                    "gender": s["eligibility"]["gender"],
                    "min_qualification": s["eligibility"]["min_qualification"],
                    "state": s["eligibility"]["state"],
                    "occupation": s["eligibility"]["occupation"],
                    "application_url": s["application_url"]
                }
                for s in schemes
            ]

            embeddings = self.embedder.encode(documents, convert_to_numpy=True).tolist()
            self.schemes_collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"[RAGEngine] Successfully indexed {len(schemes)} schemes.")
        else:
            print(f"[RAGEngine] Schemes collection already contains {existing_schemes_count} items.")

        # Index Jobs
        jobs = DatasetLoader.load_jobs(reload=force_reload)
        existing_jobs_count = self.jobs_collection.count()
        if existing_jobs_count == 0 or force_reload:
            print(f"[RAGEngine] Indexing {len(jobs)} jobs into vector DB...")
            if existing_jobs_count > 0:
                self.chroma_client.delete_collection("government_jobs")
                self.jobs_collection = self.chroma_client.get_or_create_collection(
                    name="government_jobs",
                    metadata={"hnsw:space": "cosine"}
                )

            ids = [j["job_id"] for j in jobs]
            documents = [j["search_text"] for j in jobs]
            metadatas = [
                {
                    "title_en": j["title_en"],
                    "title_hi": j["title_hi"],
                    "organization": j["organization"],
                    "qualification_required": j["qualification_required"],
                    "min_age": j["min_age"],
                    "max_age": j["max_age"],
                    "vacancies": j["vacancies"],
                    "deadline": j["application_deadline"],
                    "official_portal": j["official_portal"],
                    "location": j.get("location", "All India")
                }
                for j in jobs
            ]

            embeddings = self.embedder.encode(documents, convert_to_numpy=True).tolist()
            self.jobs_collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"[RAGEngine] Successfully indexed {len(jobs)} jobs.")
        else:
            print(f"[RAGEngine] Jobs collection already contains {existing_jobs_count} items.")

    def search_schemes(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Semantic search for schemes matching query in English, Hindi, or regional languages."""
        query_embedding = self.embedder.encode([query], convert_to_numpy=True).tolist()[0]
        results = self.schemes_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        matches = []
        schemes_lookup = {s["id"]: s for s in DatasetLoader.load_schemes()}
        if results and "ids" in results and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if "distances" in results else 0.0
                # In cosine space, similarity = 1 - distance
                similarity = max(0.0, 1.0 - distance)
                scheme_data = schemes_lookup.get(doc_id, {})
                matches.append({
                    "scheme_id": doc_id,
                    "title_en": results["metadatas"][0][i].get("title_en"),
                    "title_hi": results["metadatas"][0][i].get("title_hi"),
                    "category": results["metadatas"][0][i].get("category"),
                    "summary_en": scheme_data.get("summary_en"),
                    "summary_hi": scheme_data.get("summary_hi"),
                    "benefits_en": scheme_data.get("benefits_en"),
                    "benefits_hi": scheme_data.get("benefits_hi"),
                    "documents_required": scheme_data.get("documents_required", []),
                    "application_url": results["metadatas"][0][i].get("application_url"),
                    "similarity_score": round(similarity, 4)
                })
        return matches

    def search_jobs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Semantic search for jobs matching query in English, Hindi, or regional languages."""
        query_embedding = self.embedder.encode([query], convert_to_numpy=True).tolist()[0]
        results = self.jobs_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        matches = []
        jobs_lookup = {j["job_id"]: j for j in DatasetLoader.load_jobs()}
        if results and "ids" in results and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if "distances" in results else 0.0
                similarity = max(0.0, 1.0 - distance)
                job_data = jobs_lookup.get(doc_id, {})
                matches.append({
                    "job_id": doc_id,
                    "title_en": results["metadatas"][0][i].get("title_en"),
                    "title_hi": results["metadatas"][0][i].get("title_hi"),
                    "organization": results["metadatas"][0][i].get("organization"),
                    "qualification_required": results["metadatas"][0][i].get("qualification_required"),
                    "vacancies": results["metadatas"][0][i].get("vacancies"),
                    "application_deadline": results["metadatas"][0][i].get("deadline"),
                    "official_portal": results["metadatas"][0][i].get("official_portal"),
                    "summary_en": job_data.get("summary_en"),
                    "summary_hi": job_data.get("summary_hi"),
                    "similarity_score": round(similarity, 4)
                })
        return matches
