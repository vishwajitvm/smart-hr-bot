# backend/app/models/candidate_chat.py
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any
from datetime import datetime

class CandidateChatModel(BaseModel):
    # Pydantic v2 config
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True,
    )

    candidate_id: str
    job_id: str
    question: Optional[str] = None
    response: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='before')
    @classmethod
    def extract_ids(cls, values):
        """
        Extract candidate_id and job_id from nested payload if needed
        """
        if "candidate" in values:
            candidate_data = values["candidate"]
            if isinstance(candidate_data, dict):
                values["candidate_id"] = candidate_data.get("id") or values.get("candidate_id")
        if "job" in values:
            job_data = values["job"]
            if isinstance(job_data, dict):
                values["job_id"] = job_data.get("id") or values.get("job_id")
        return values
