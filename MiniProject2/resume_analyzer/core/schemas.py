from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional, Dict
from datetime import datetime


class ResumeUploadInput(BaseModel):
    file: bytes = Field(description="Resume file in PDF or DOCX format")
    job_id: Optional[str] = Field(default=None, description="ID of the job listing to match against")

    @field_validator("file")
    @classmethod
    def validate_file(cls, value: bytes) -> bytes:
        if not isinstance(value, bytes):
            raise ValueError("File must be provided as bytes")
        if len(value) == 0:
            raise ValueError("File cannot be empty")
        if not (value.startswith(b'%PDF') or value.startswith(b'\x50\x4B\x03\x04')):
            raise ValueError("File must be a PDF or DOCX")
        return value

    model_config = {"str_strip_whitespace": True}


class ResumeAnalysisOutput(BaseModel):
    skills: List[str] = Field(default_factory=list)
    formatting: bool
    word_count: int = Field(ge=0)
    skill_density: float = Field(ge=0.0)
    suggestions: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=100.0)

    model_config = {"json_encoders": {float: lambda v: round(v, 2)}}


class ResumeResponse(BaseModel):
    resume_id: str = Field(description="Unique ID of the resume")
    user_id: int = Field(description="ID of the user who uploaded the resume")
    analysis: ResumeAnalysisOutput = Field(description="Analysis results of the resume")
    score: float = Field(ge=0.0, le=100.0, description="Overall score of the resume")

    model_config = {"json_encoders": {float: lambda v: round(v, 2)}}


class ResumeResponseList(BaseModel):
    resume_id: str = Field(description="Unique ID of the resume")
    score: float = Field(ge=0.0, le=100.0, description="Overall score of the resume")

    model_config = {"json_encoders": {float: lambda v: round(v, 2)}}


class JobListingCreate(BaseModel):
    title: str = Field(max_length=200, description="Title of the job listing")
    description: str = Field(max_length=2000, description="Job description")
    skills_required: Dict[str, List[str]] = Field(description="Required skills, e.g., {'skills': ['Python', 'SQL']}")

    model_config = {"str_strip_whitespace": True}


class JobListingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200, description="Updated title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Updated description")
    skills_required: Optional[Dict[str, List[str]]] = Field(default=None, description="Updated required skills")

    model_config = {"str_strip_whitespace": True}


class JobListingResponse(BaseModel):
    job_id: int = Field(description="Unique ID of the job listing")
    title: str
    description: str
    skills_required: Dict[str, List[str]]
    recruiter_id: int
    created_at: datetime
    updated_at: datetime


class UserRegisterInput(BaseModel):
    username: str = Field(max_length=150, description="Unique username")
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="Password (min 8 characters)")
    role: str = Field(description="User role", pattern="^(job_seeker|recruiter|admin)$")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value

    model_config = {"str_strip_whitespace": True}


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    message: str


class VerifyEmailInput(BaseModel):
    token: str = Field(description="Verification token sent to email")
