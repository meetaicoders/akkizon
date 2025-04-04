# external imports
from fastapi import APIRouter, HTTPException, Depends, Request

# internal imports
from core.logger import setup_logger
from modules.authentication.helpers import get_authenticated_user
from modules.authentication.schemas import AuthenticatedUser
from modules.integration.dependencies import get_connector_client
from modules.integration.clients import ConnectorClient
from modules.integration.schemas import (
    DeleteConnectorOfUserRequest
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/v1/integration", tags=["integration"])

@router.post("/fetch-default-connectors")
async def fetch_default_connectors(
    user: AuthenticatedUser = Depends(get_authenticated_user), 
    connector_client: ConnectorClient = Depends(get_connector_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await connector_client.fetch_default_connectors()

@router.post("/fetch_all_connectors_for_user")
async def fetch_all_connectors_for_user(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    connector_client: ConnectorClient = Depends(get_connector_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await connector_client.fetch_all_connectors_for_user(user.user.id, user.organization.id, user.project.id)

@router.post("/delete_connector_of_user")
async def delete_connector_of_user(
    request: DeleteConnectorOfUserRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
    connector_client: ConnectorClient = Depends(get_connector_client)
    ):
    if not user.success:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await connector_client.delete_connector_of_user(
        connector_id=request.connector_id,
        organization_id=user.organization.id,
        user_id=user.user_id,
        project_id=request.project_id
    )