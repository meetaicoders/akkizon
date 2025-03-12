from fastapi import APIRouter, Depends
from modules.authentication.helpers import get_authenticated_user
from modules.authentication.schemas import AuthenticatedUser

router = APIRouter()

@router.get("/verify-user")
def verify_user(user: AuthenticatedUser = Depends(get_authenticated_user)):
    return user
