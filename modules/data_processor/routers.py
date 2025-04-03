# external imports
from fastapi import APIRouter, HTTPException, Depends, Request

# internal imports
from core.logger import setup_logger
from modules.authentication.helpers import get_authenticated_user
from modules.authentication.schemas import AuthenticatedUser
from modules.data_processor.helpers import get_connector_client, get_project_client, get_hubspot_connector
from modules.data_processor.clients import ConnectorClient, ProjectClient, HubSpotConnector
from modules.data_processor.schemas import (
    AddProjectRequest, 
    FetchProjectByIdRequest
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/v1/data", tags=["data_processor"])

@router.post("/fetch-default-connectors")
async def fetch_default_connectors(
    user: AuthenticatedUser = Depends(get_authenticated_user), 
    connector_client: ConnectorClient = Depends(get_connector_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return connector_client.fetch_default_connectors()

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


@router.post("/initiate-oauth-flow")
async def initiate_oauth_flow(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    hubspot_connector: HubSpotConnector = Depends(get_hubspot_connector)
    ):
    """Initiate HubSpot OAuth flow"""
    return await hubspot_connector.initiate_oauth_flow()

@router.get("/hubspot-oauth-callback")
async def hubspot_oauth_callback(request: Request):
    """Handle HubSpot OAuth callback"""
    # Get code from request
    code = request.query_params.get('code')
    print(code)
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    hubspot_connector = HubSpotConnector()
    return await hubspot_connector.exchange_code(code)