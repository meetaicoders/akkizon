"""
Data Extraction

Extracts data from different sources (e.g., Snowflake, HubSpot, Postgres). 
Uses a Factory Pattern to determine which extractor to use.

Classes & Functions:
    ExtractorFactory
        get_extractor(integration_type: str)
            Returns the appropriate extractor class.

    SnowflakeExtractor
        extract(query: str) -> list
            Fetch data from Snowflake based on query.

Usage Example:
    extractor = ExtractorFactory.get_extractor("snowflake")
    data = extractor.extract("SELECT * FROM users")
"""

import snowflake.connector

class SnowflakeExtractor:
    """Extract data from Snowflake."""
    
    def extract(self, query: str) -> list:
        conn = snowflake.connector.connect(
            user="your_user",
            password="your_password",
            account="your_account"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

class HubSpotExtractor:
    """Extract data from HubSpot."""
    
    def extract(self, query: str) -> list:
        # Simulated API call
        return [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Doe"}]
