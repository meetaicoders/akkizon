"""
Data Loading

Loads cleaned data into the target database (e.g., Snowflake, Postgres). 
Uses batch inserts for efficiency.

Classes & Functions:
    SnowflakeLoader
        load(data: list, table: str)
            Insert transformed data into Snowflake.

Usage Example:
    loader = SnowflakeLoader()
    loader.load(cleaned_data, "target_table")
"""
import snowflake.connector

class SnowflakeLoader:
    """Load data into Snowflake."""
    
    def load(self, data: list, table: str):
        conn = snowflake.connector.connect(
            user="your_user",
            password="your_password",
            account="your_account"
        )
        cursor = conn.cursor()
        
        for row in data:
            values = ", ".join([f"'{str(value)}'" for value in row])
            query = f"INSERT INTO {table} VALUES ({values})"
            cursor.execute(query)

        conn.commit()
        conn.close()
        print(f"Data successfully loaded into {table}")

class HubSpotLoader:
    """Mock loader for HubSpot (for demonstration)."""
    
    def load(self, data: list, table: str):
        print(f"Simulated loading {len(data)} records into {table} in HubSpot.")
