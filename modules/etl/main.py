"""
ETL Runner

Entry point for ETL execution (manual or API-triggered). Detects integration type 
(e.g., HubSpot, Snowflake) and orchestrates the extract → transform → load process.

Key Functions:
    run_etl(integration_type: str, query: str, table: str)
        Calls Extractor, Cleaner, and Loader in sequence.

Usage Example (Manual Run):
    python modules/etl/main.py

Usage Example (API Trigger):
    import requests
    requests.post("http://localhost:8000/api/etl/run/", json={
        "integration": "hubspot",
        "query": "SELECT * FROM contacts",
        "table": "target_table"
    })
"""
from modules.etl.factory import ExtractorFactory, LoaderFactory
from modules.etl.transform import DataCleaner

def run_etl(integration_type: str, query: str, table: str):
    """Run the ETL pipeline for a given integration and query."""
    print(f"Starting ETL for {integration_type}...")

    # Extract Data
    extractor = ExtractorFactory.get_extractor(integration_type)
    raw_data = extractor.extract(query)

    # Transform Data
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean(raw_data)

    # Load Data
    loader = LoaderFactory.get_loader(integration_type)
    loader.load(cleaned_data, table)

    print(f"ETL for {integration_type} completed successfully.")

if __name__ == "__main__":
    # Example: Running for Snowflake
    run_etl("snowflake", "SELECT * FROM users", "target_table")
