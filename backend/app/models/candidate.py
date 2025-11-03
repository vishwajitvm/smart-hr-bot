# app/models/candidate.py
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from typing import Optional, List, Dict, Any, Union

class CandidateBase(BaseModel):
    # Pydantic v2 config
    model_config = ConfigDict(extra='allow')

    name: Optional[str] = ""
    email: Optional[EmailStr] = None
    phone: Optional[str] = ""
    location: Optional[str] = ""
    # years_of_experience: Optional[str] = ""
    years_of_experience: Optional[Union[str, int]] = ""

    # avoid mutable defaults
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)

    experience_summary: Optional[str] = ""
    position: Optional[str] = ""
    job_id: Optional[str] = None
    status: Optional[str] = "active"
    deleted: Optional[bool] = False

    resume_id: Optional[str] = None
    resume_url: Optional[str] = None
    
    # Candidate progression statuses
    # 0 = Pending, 1 = Approved, 2 = Rejected
    stage_resume_review_status: int = 0
    stage_ai_voice_call_status: int = 0
    stage_ai_screening_status: int = 0


    # bucket for any extra/unstructured fields (projects, education, etc.)
    extra_data: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def move_extras_to_extra_data(cls, values):
        if not isinstance(values, dict):
            return values
        defined = set(cls.model_fields.keys())
        extra = {k: v for k, v in values.items() if k not in defined}
        base = {k: v for k, v in values.items() if k in defined}
        if extra:
            base['extra_data'] = {**base.get('extra_data', {}), **extra}
        return base


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: str
