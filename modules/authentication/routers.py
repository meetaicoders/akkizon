from fastapi import APIRouter, Depends, Body, HTTPException, Request
from fastapi.responses import JSONResponse
from modules.authentication.helpers import (
    get_authenticated_user, 
    get_authenticated_user_without_org, 
    get_organization_handler,
    get_auth_handler,
    get_profile_client
)
from modules.authentication.schemas import (
    AuthenticatedUser,
    Organization,
    Profile
)

router = APIRouter()

@router.get("/verify-user")
def verify_user(user: AuthenticatedUser = Depends(get_authenticated_user)):
    return user

@router.post("/add-organization")
def add_organization(
    user: AuthenticatedUser = Depends(get_authenticated_user_without_org),
    organization: Organization = Body(...),
    profile: Profile = Body(...)
):
    try:
        organization_handler = get_organization_handler()
        profile_client = get_profile_client()
        new_organization = organization_handler.generate_organization_for_user(user, organization)
        if new_organization.id:
            profile_client.update_default_organization(user.user_id, profile.name, new_organization.id)
        return new_organization
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-user-organizations")
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
    
@router.get("/fetch-user-profile")
def fetch_user_profile(
    user: AuthenticatedUser = Depends(get_authenticated_user_without_org)
):
    profile_client = get_profile_client()
    profile = profile_client.fetch_user_profile(user.user_id)
    return profile

@router.post("/update-default-organization")
def update_default_organization(
    user: AuthenticatedUser = Depends(get_authenticated_user_without_org),
    profile: Profile = Body(...)
):
    profile_client = get_profile_client()
    profile_client.update_default_organization(user.user_id, profile.name, profile.default_organization)
    return JSONResponse(content={"message": "Default organization updated successfully"})