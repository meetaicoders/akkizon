"""
Factory Pattern for Auto-Detection

Dynamically selects the right extractor and loader based on integration type.

Classes & Functions:
    ExtractorFactory
        get_extractor(integration_type: str)
            Returns the appropriate extractor class.

Usage Example:
    extractor = ExtractorFactory.get_extractor("hubspot")
"""
from modules.etl.extract import SnowflakeExtractor, HubSpotExtractor
from modules.etl.load import SnowflakeLoader, HubSpotLoader

class ExtractorFactory:
    """Factory to get the appropriate data extractor."""
    
    @staticmethod
    def get_extractor(integration_type: str):
        if integration_type == "snowflake":
            return SnowflakeExtractor()
        elif integration_type == "hubspot":
            return HubSpotExtractor()
        else:
            raise ValueError(f"Unsupported integration: {integration_type}")

class LoaderFactory:
    """Factory to get the appropriate data loader."""
    
    @staticmethod
    def get_loader(integration_type: str):
        if integration_type == "snowflake":
            return SnowflakeLoader()
        elif integration_type == "hubspot":
            return HubSpotLoader()
        else:
            raise ValueError(f"Unsupported integration: {integration_type}")
