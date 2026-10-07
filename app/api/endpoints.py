from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from pydantic import BaseModel

from app.core.schemas import UserProfileInput
from app.ml.rag_engine import MultilingualRAGEngine
from app.ml.matcher import EligibilityMatcher
from app.services.ocr_service import DocumentOCRService
from app.services.document_analyzer import DocumentAnalyzer
from app.ml.data_loader import DatasetLoader

router = APIRouter(prefix="/api", tags=["Government Assistant Services"])

class SearchQueryRequest(BaseModel):
    query: str
    top_k: int = 3
    category_filter: Optional[str] = None

@router.post("/eligibility/check", summary="Check citizen scheme & job eligibility")
async def check_eligibility(profile: UserProfileInput):
    """
    Evaluates citizen's qualification, age, income, and category against all
    official schemes and job vacancies using our trained neural matcher.
    """
    matcher = EligibilityMatcher.get_instance()
    results = matcher.match_all(profile)
    return results

@router.post("/schemes/search", summary="Multilingual semantic search for schemes & jobs")
async def search_schemes_and_jobs(req: SearchQueryRequest):
    """
    Performs vector semantic search in English, Hindi, or regional languages.
    """
    rag = MultilingualRAGEngine.get_instance()
    schemes = rag.search_schemes(req.query, top_k=req.top_k)
    jobs = rag.search_jobs(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "matched_schemes": schemes,
        "matched_jobs": jobs
    }

@router.post("/documents/upload-and-explain", summary="Upload document for OCR and plain language explanation")
async def upload_and_explain_document(
    file: UploadFile = File(...),
    preferred_language: str = Form("hi")
):
    """
    Accepts official notice/circular (PDF or Image), runs OCR to extract text,
    matches against the RAG database, and explains it in simple language.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        ocr_service = DocumentOCRService.get_instance()
        ocr_result = ocr_service.process_file(contents, filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    analyzer = DocumentAnalyzer.get_instance()
    analysis = analyzer.analyze_document(
        ocr_result["extracted_text"],
        preferred_language=preferred_language
    )

    return {
        "file_info": ocr_result,
        "analysis": analysis
    }

@router.get("/jobs/recent", summary="Get recent government job recruitment notifications")
async def get_recent_jobs(
    qualification: Optional[str] = Query(None, description="Filter by qualification: 10th, 12th, Graduate, etc.")
):
    """
    Lists recent government job vacancies with details, deadlines, and official links.
    """
    all_jobs = DatasetLoader.load_jobs()
    if qualification and qualification.lower() != "all":
        filtered = [
            j for j in all_jobs 
            if j.get("qualification_required", "").lower() == qualification.lower()
        ]
        return {"total": len(filtered), "qualification_filter": qualification, "jobs": filtered}
    return {"total": len(all_jobs), "qualification_filter": "All", "jobs": all_jobs}

@router.get("/schemes/all", summary="List all cataloged government schemes")
async def get_all_schemes():
    schemes = DatasetLoader.load_schemes()
    return {"total": len(schemes), "schemes": schemes}

from app.services.profile_service import ProfileManager

@router.get("/profile", summary="Get citizen profile, applications, exams, and bookmarks")
async def get_citizen_profile():
    return ProfileManager.get_profile()

@router.post("/profile", summary="Update citizen personal profile")
async def update_citizen_profile(profile_data: Dict[str, Any]):
    ProfileManager.save_profile(profile_data)
    return {"status": "success", "message": "Profile updated successfully"}

@router.post("/profile/applications", summary="Add new application form to profile tracker")
async def add_application_to_profile(app_data: Dict[str, Any]):
    ProfileManager.add_application(app_data)
    return {"status": "success", "message": "Application added to profile"}

@router.post("/profile/exams", summary="Add new past exam and result record")
async def add_exam_to_profile(exam_data: Dict[str, Any]):
    ProfileManager.add_exam(exam_data)
    return {"status": "success", "message": "Exam record added to profile"}

from app.services.auth_service import AuthService

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = ""
    age: Optional[int] = 21
    gender: Optional[str] = "Male"
    qualification: Optional[str] = "12th"
    category: Optional[str] = "General"
    state: Optional[str] = "All India"
    occupation: Optional[str] = "Student"

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/register", summary="Register new citizen account")
async def register_account(req: RegisterRequest):
    res = AuthService.register(
        name=req.name,
        email=req.email,
        password=req.password,
        phone=req.phone or "",
        age=req.age or 21,
        gender=req.gender or "Male",
        qualification=req.qualification or "12th",
        category=req.category or "General",
        state=req.state or "All India",
        occupation=req.occupation or "Student"
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.post("/auth/login", summary="Citizen login")
async def login_account(req: LoginRequest):
    res = AuthService.login(req.email, req.password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["message"])
    return res
