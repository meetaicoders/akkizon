from app.modules.data_processor.handlers import DatasetHandler

"""
Data Visualization Service

Converts processed data into frontend-friendly JSON format for charting.
"""

from typing import Dict, Any
import pandas as pd
from app.modules.data_processor.services import DataPreProcessor
import logging

logger = logging.getLogger(__name__)

class DataVisualizationService:
    def __init__(self, processor: DatasetHandler):
        self.processor = processor
        
    def get_chart_data(self, raw_data: str) -> Dict[str, Any]:
        """
        Process raw data into chart-ready JSON format.
        
        Args:
            raw_data: Input data in string format
            
        Returns:
            Dictionary with columns, data, and metadata
        """
        try:
            if not self.processor.validate_input_data(raw_data):
                raise ValueError("Invalid input data")
            
            # Process data through existing pipeline
            df = self.processor.convert_to_dataframe(raw_data)
            
            # Convert DataFrame to frontend-friendly format
            return {
                "columns": df.columns.tolist(),
                "data": df.to_dict(orient="records"),
                "metadata": self._calculate_metadata(df)
            }
            
        except Exception as e:
            logger.error(f"Data visualization failed: {str(e)}")
            raise

    def _calculate_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistics and dataset metadata"""
        stats = {}
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            stats[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "count": int(df[col].count())
            }
            
        return {
            "row_count": len(df),
            "statistics": stats,
            "column_types": dict(df.dtypes.apply(lambda x: x.name))
        }