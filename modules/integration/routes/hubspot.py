# external imports
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

# internal imports
from core.logger import setup_logger
from modules.authentication.helpers import get_authenticated_user
from modules.authentication.schemas import AuthenticatedUser
from modules.integration.dependencies import get_hubspot_connector_client
from modules.integration.clients import HubSpotConnector
from modules.integration.schemas import (
    HubSpotCallbackQueryParams
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/v1/integration/hubspot", tags=["hubspot"])

@router.post("/initiate-oauth-flow")
async def initiate_oauth_flow(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    hubspot_connector: HubSpotConnector = Depends(get_hubspot_connector_client)
    ):
    """Initiate HubSpot OAuth flow"""
    oauth_url = await hubspot_connector.initiate_oauth_flow()
    return JSONResponse(
        content={"url": oauth_url},
        status_code=200
    )

@router.get("/oauth-callback")
async def hubspot_oauth_callback(
    params: HubSpotCallbackQueryParams = Depends(),
    user: AuthenticatedUser = Depends(get_authenticated_user),
    hubspot_connector: HubSpotConnector = Depends(get_hubspot_connector_client)
    ):
    """Handle HubSpot OAuth callback"""
    # Get code from request
    try:
        # Process the callback
        if params.error:
            raise HTTPException(
                status_code=400,
                detail=f"Authorization failed: {params.error}"
            )
        
        # Exchange code for tokens
        token_data = await hubspot_connector.exchange_code(
            code=params.code, 
            state=params.state, 
            connector_id=params.connector_id, 
            organization_id=user.organization.id, 
            user_id=user.user_id, 
            project_id=params.project_id)
        
        return JSONResponse(
            content={"message": "HubSpot account connected successfully"},
            status_code=200
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )