from fastapi import APIRouter, Depends, Body, HTTPException
from modules.authentication.helpers import (
    get_authenticated_user, 
    get_authenticated_user_without_org, 
    get_organization_handler,
    get_auth_handler
)
from modules.authentication.schemas import (
    AuthenticatedUser,
    Organization
)

router = APIRouter()

@router.get("/verify-user")
def verify_user(user: AuthenticatedUser = Depends(get_authenticated_user)):
    return user

@router.post("/add-organization")
def add_organization(
    user: AuthenticatedUser = Depends(get_authenticated_user_without_org),
    organization: Organization = Body(...)
):
    try:
        organization_handler = get_organization_handler()
        new_organization = organization_handler.generate_organization_for_user(user, organization)
        return new_organization
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-user-organizations")
def get_user_organizations(
    user: AuthenticatedUser = Depends(get_authenticated_user_without_org)
):
    try:
        organization_handler = get_organization_handler()
        organizations = organization_handler.get_user_organizations(user)
        return organizations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/sign-in')
def sign_in(
    email: str = Body(...),
    password: str = Body(...)
):
    auth_handler = get_auth_handler().auth_client.sign_in(email=email, password=password)
    return auth_handler
    
