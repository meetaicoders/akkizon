# external imports
from pydantic import BaseModel
from typing import Optional

class AuthenticatedUser(BaseModel):
    success: bool
    user_id: Optional[str] = None
    organization_id: Optional[str] = None