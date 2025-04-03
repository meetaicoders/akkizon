from modules.data_processor.clients import ConnectorClient, ProjectClient, HubSpotConnector

def get_connector_client() -> ConnectorClient:
    """
    Get the connector client.
    """
    return ConnectorClient()

def get_project_client() -> ProjectClient:
    """
    Get the project client.
    """
    return ProjectClient()

def get_hubspot_connector() -> HubSpotConnector:
    """
    Get the hubspot connector.
    """
    return HubSpotConnector()