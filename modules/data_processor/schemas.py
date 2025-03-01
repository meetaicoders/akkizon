from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class DataFrameRow(BaseModel):
    """Validated data structure for DataFrame rows"""
    data: Dict[str, str|float]
    confidence: float
    processing_notes: List[str]

class ConversionRequest(BaseModel):
    raw_data: str
    format_hint: Optional[str] = None

class FilterRequest(BaseModel):
    dataframe: Dict[str, List]  # JSON-serialized DataFrame
    filter_config: Optional[Dict] = None

class NormalizationRequest(BaseModel):
    dataframe: Dict[str, List]  # JSON-serialized DataFrame
    normalization_type: Optional[str] = "auto"

class PipelineRequest(BaseModel):
    raw_data: str
    steps: List[Dict[str, Any]]
