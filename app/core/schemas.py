from typing import List, Optional
from pydantic import BaseModel, Field

class EligibilityCriteria(BaseModel):
    min_age: int = 0
    max_age: int = 100
    gender: str = "All"  # "All", "Female", "Male"
    min_qualification: str = "None"  # "None", "8th", "10th", "12th", "Diploma", "Graduate", "Post Graduate"
    max_annual_income: Optional[int] = None  # in INR
    caste_category: List[str] = ["All"]  # "All", "General", "OBC", "SC", "ST", "EWS"
    state: str = "All India"
    occupation: str = "Any"  # "Farmer", "Student", "Artisan", "Unemployed", "Self-employed", "Any"

class SchemeRecord(BaseModel):
    id: str
    title_en: str
    title_hi: str
    category: str
    summary_en: str
    summary_hi: str
    eligibility: EligibilityCriteria
    benefits_en: str
    benefits_hi: str
    documents_required: List[str]
    application_url: str
    tags: List[str] = []

class JobNotificationRecord(BaseModel):
    job_id: str
    title_en: str
    title_hi: str
    organization: str
    category: str
    qualification_required: str  # "10th", "12th", "Diploma", "Graduate", "Post Graduate"
    min_age: int = 18
    max_age: int = 40
    vacancies: str
    application_deadline: str
    official_portal: str
    summary_en: str
    summary_hi: str
    location: str = "All India"

class UserProfileInput(BaseModel):
    age: int
    gender: str = "All"
    qualification: str  # "None", "10th", "12th", "Diploma", "Graduate", "Post Graduate"
    annual_income: Optional[int] = None
    caste_category: str = "General"
    state: str = "All India"
    occupation: str = "Any"
    interests_or_query: Optional[str] = None
    preferred_language: str = "hi"  # "en", "hi", etc.
