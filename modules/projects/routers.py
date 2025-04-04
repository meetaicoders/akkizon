# external imports
from fastapi import APIRouter, HTTPException, Depends, Request

# internal imports
from core.logger import setup_logger
from modules.authentication.helpers import get_authenticated_user
from modules.authentication.schemas import AuthenticatedUser
from modules.projects.dependencies import get_project_client
from modules.projects.clients import ProjectClient
from modules.projects.schemas import (
    AddProjectRequest, 
    FetchProjectByIdRequest
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/v1/projects", tags=["projects"])

@router.post("/add-project")
async def add_project(
    project_data: AddProjectRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
    project_client: ProjectClient = Depends(get_project_client)
    ):

    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not project_data.project_id:
        raise HTTPException(status_code=400, detail="Project ID is required")
    try:
        response = project_client.add_project(
            project_data.project_id, 
            project_data.name, 
            user.user_id, 
            user.organization_id
        )
        return response[0]
    except Exception as e:
        logger.error(f"Failed to add project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-project-by-id")
async def fetch_project_by_id(
    project_data: FetchProjectByIdRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
    project_client: ProjectClient = Depends(get_project_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        response = project_client.fetch_project_by_id(project_data.project_id)
    except Exception as e:
        logger.error(f"Failed to fetch project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    if not response:
        raise HTTPException(status_code=404, detail="Project not found")
    return response[0]

@router.post("/fetch-all-projects-by-organization")
async def fetch_all_projects_by_organization(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    project_client: ProjectClient = Depends(get_project_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        response = project_client.fetch_all_projects_by_organization(
            user.user_id, 
            user.organization_id
        )
    except Exception as e:
        logger.error(f"Failed to fetch all projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    if not response:
        raise HTTPException(status_code=404, detail="No projects found")
    return response