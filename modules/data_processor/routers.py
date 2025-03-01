from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import logging
from app.modules.data_processor import (
    DatasetHandler,
    DataVisualizationService,
    ConversionRequest,
    FilterRequest,
    NormalizationRequest,
    PipelineRequest
)


router = APIRouter(prefix="/data", tags=["data_processing"])
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chart-data")
async def get_visualization_data(raw_data: str):
    """
    Endpoint for retrieving processed data in chart-friendly format
    
    Example payload:
    {
        "raw_data": "text: 5kg, price: $20..."
    }
    """
    try:
        handler  = DatasetHandler()
        visualization_service = DataVisualizationService(handler)
        return visualization_service.get_chart_data(raw_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chart data: {str(e)}"
        )
    
    
@router.post("/convert")
async def convert_data(request: ConversionRequest):
    """Convert raw data to structured format using AI analysis"""
    try:
        handler  = DatasetHandler()
        df = handler.convert_to_dataframe(request.raw_data)
        return {
            "status": "success",
            "data": df.to_dict(orient="records"),
            "columns": list(df.columns)
        }
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter")
async def filter_data(request: FilterRequest):
    """Apply AI-powered anomaly detection and filtering"""
    try:
        handler  = DatasetHandler()
        df = pd.DataFrame(request.dataframe)
        filtered_df = handler.filter_anomalies(df)
        return {
            "status": "success",
            "data": filtered_df.to_dict(orient="records"),
            "removed_records": len(df) - len(filtered_df)
        }
    except Exception as e:
        logger.error(f"Filtering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalize")
async def normalize_data(request: NormalizationRequest):
    """Apply AI-suggested normalization methods"""
    try:
        handler  = DatasetHandler()
        df = pd.DataFrame(request.dataframe)
        normalized_df = handler.normalize_data(df)
        return {
            "status": "success",
            "data": normalized_df.to_dict(orient="records"),
            "transformations_applied": len(normalized_df.columns)
        }
    except Exception as e:
        logger.error(f"Normalization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline")
async def execute_pipeline(request: PipelineRequest):
    """Execute a complete processing pipeline"""
    try:
        handler  = DatasetHandler()
        
        # Configure pipeline steps
        for step in request.steps:
            handler.add_step(step['name'], step.get('config', {}))
            
        # Execute and get result
        df = handler.execute_pipeline(request.raw_data)
        
        return {
            "status": "success",
            "data": df.to_dict(orient="records"),
            "steps_executed": len(request.steps)
        }
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
