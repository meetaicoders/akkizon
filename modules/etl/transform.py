"""
Data Transformation

Cleans, validates, and preprocesses data before loading. Handles null values, 
duplicates, and data formatting.

Classes & Functions:
    DataCleaner
        clean(data: list) -> list
            Remove duplicates, handle missing values, normalize formats.

Usage Example:
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean(raw_data)
"""
class DataCleaner:
    """Cleans raw data by handling nulls, duplicates, and formatting."""
    
    def clean(self, data: list) -> list:
        cleaned_data = []
        seen = set()
        
        for row in data:
            # Remove duplicates
            row_tuple = tuple(row.items()) if isinstance(row, dict) else tuple(row)
            if row_tuple in seen:
                continue
            seen.add(row_tuple)

            # Handle missing values (Example: Replace None with 'N/A')
            cleaned_row = {key: (value if value is not None else "N/A") for key, value in row.items()} if isinstance(row, dict) else row
            cleaned_data.append(cleaned_row)
        
        return cleaned_data
