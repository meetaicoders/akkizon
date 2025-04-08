from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID

class AddProjectRequest(BaseModel):
    name: Optional[str] = None
    project_id: Optional[str] = None

    @field_validator('project_id')
    def validate_project_id(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v
    
class FetchProjectByIdRequest(BaseModel):
    project_id: str

    @field_validator('project_id')
    def validate_project_id(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v