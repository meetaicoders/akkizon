# External imports
from typing import List, Dict, Any

# Internal imports
from utils.helper_funcs import get_supabase_client
from core.logger import setup_logger
from modules.authentication.clients import BigDataOAuthClient
from core.config import settings

logger = setup_logger(__name__)


class ConnectorClient:
    """
    A client for fetching connectors from the database.
    """
    def __init__(self, data_connector_table: str = "data_connectors", user_connector_table: str = "user_connectors"):
        self.client = get_supabase_client()
        self.data_connector_table  = data_connector_table
        self.user_connector_table = user_connector_table

    async def fetch_default_connectors(self) -> List[Dict[str, Any]]:
        """
        Fetch all default connectors from the database.
        Args:
            None
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing connector information.
        """
        try:
            logger.info(f"Fetching default connectors...")
            response = self.client.table(self.data_connector_table).select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch default connectors: {str(e)}")
            raise e
    
    async def fetch_all_connectors_for_user(self, user_id: str, organization_id: str, project_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all connectors for a user.

        Args:
            user_id: str
            organization_id: str
            project_id: str
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing connector information.
        """
        try:
            logger.info(f"Fetching connectors for user {user_id}...")
            response = (
                self.client.table(self.user_connector_table)
                .select("*")
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .eq("project_id", project_id)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch connectors: {str(e)}")
            raise e
    
    async def delete_connector_of_user(self, connector_id: str, organization_id: str, user_id: str, project_id: str) -> None:
        """
        Delete a connector of a user.
        Args:
            connector_id: str
            organization_id: str
            user_id: str
            project_id: str
        """
        try:
            logger.info(f"Deleting connector {connector_id} for user {user_id}...")
            self.client.table(self.user_connector_table).delete().eq("connector_id", connector_id).eq("organization_id", organization_id).eq("user_id", user_id).eq("project_id", project_id).execute()
        except Exception as e:
            logger.error(f"Failed to delete connector: {str(e)}")
            raise e
        
class HubSpotConnector(BigDataOAuthClient):
    """
    A client for HubSpot connectors. Inherits from BigDataOAuthClient. Perform operations on the HubSpot API.
    """
    def __init__(self):
        super().__init__(
            client=get_supabase_client(),
            client_id=settings.hubspot_client_id,
            client_secret=settings.hubspot_client_secret,
            redirect_uri=settings.hubspot_redirect_uri,
            auth_url="https://app.hubspot.com/oauth/authorize",
            token_url="https://api.hubapi.com/oauth/v1/token"
        )
    
    async def initiate_oauth_flow(self) -> str:
        """
        Initiate the OAuth flow.
        """
        return await super().initiate_oauth_flow()

    async def exchange_code(self, 
                            code: str, 
                            state: str, 
                            connector_id: str, 
                            organization_id: str, 
                            user_id: str, 
                            project_id: str) -> Dict[str, Any]:
        """
        Exchange the code for an access token.
        """
        return await super().exchange_code(code, state, connector_id, organization_id, user_id, project_id)

    async def refresh_access_token(self, connector_id: str, organization_id: str, user_id: str, project_id: str) -> Dict[str, Any]:
        """
        Refresh the access token.
        """
        return await super().refresh_access_token(connector_id, organization_id, user_id, project_id)

    async def get_access_token(self, connector_id: str, organization_id: str, user_id: str, project_id: str) -> Dict[str, Any]:
        """
        Get the access token.
        """
        return await super().get_access_token(connector_id, organization_id, user_id, project_id)
