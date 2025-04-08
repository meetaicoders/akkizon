from pydantic import BaseModel, Field

class DeleteConnectorOfUserRequest(BaseModel):
    connector_id: str
    project_id: str

class HubSpotCallbackQueryParams(BaseModel):
    """
    Model for HubSpot OAuth callback request.
    """
    code: str
    state: str 
    scope: str | None
    error: str | None
    project_id: str 
    connector_id: str