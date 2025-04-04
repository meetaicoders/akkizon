from modules.integration.clients import ConnectorClient, HubSpotConnector

def get_connector_client() -> ConnectorClient:
    """
    Get a connector client based on the connector type.
    """
    return ConnectorClient()

def get_hubspot_connector_client() -> HubSpotConnector:
    """
    Get a HubSpot connector client.
    """
    return HubSpotConnector()