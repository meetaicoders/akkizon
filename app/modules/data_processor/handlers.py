"""
Data Pre-Processing Services

Uses configured AI providers for intelligent data transformation tasks.
"""

from typing import List, Dict, Optional
import pandas as pd
from app.core.adapter import MultiProviderClient, ChatRequest, ChatMessage, PROVIDERS
from app.core.config import settings
import logging
from data_processor.schemas import DataFrameRow

logger = logging.getLogger(__name__)


class DatasetHandler:
    """
    This class is responsible for processing the dataset.
    methods:
    - convert_to_dataframe: Convert unstructured raw data to structured DataFrame using AI analysis.
    - filter_anomalies: Identify and remove anomalous records using AI pattern recognition.
    - normalize_data: Normalize data using AI-suggested transformations.
    - validate_input_data: Basic validation before processing.
    - add_step: Add a processing step to the pipeline.
    - execute_pipeline: Execute all steps in the pipeline sequentially.
    - clear_pipeline: Reset the processing pipeline.
    """
    def __init__(self, adapter_client: Optional[MultiProviderClient] = None):
        """
        Initialize with optional AI client.
        
        Args:
            adapter_client: Configured MultiProviderClient instance. 
                       Defaults to OpenAI if not provided.
        """
        self.client = adapter_client or MultiProviderClient(
            provider=PROVIDERS.OPENAI,
            api_key=settings.openai_api_key
        )
        self._processing_pipeline = []  # For tracking processing steps

    def convert_to_dataframe(self, raw_data: str) -> pd.DataFrame:
        """
        Convert unstructured raw data to structured DataFrame using AI analysis.
        
        Args:
            raw_data: Raw text/CSV/JSON data
            
        Returns:
            Pandas DataFrame with validated structure
            
        Example:
            >>> processor = DataPreProcessor() 
            >>> df = processor.convert_to_dataframe("text: 5kg, price: $20...")
        """
        prompt = f"""Analyze this raw data and convert it to structured JSON format:
        {raw_data}
        
        Output format:
        {{
            "columns": ["column1", "column2", ...],
            "data": [
                {{"column1": value1, "column2": value2, ...}},
                ...
            ]
        }}
        """
        
        try:
            response = self._get_ai_response(prompt)
            structured_data = self._parse_json_response(response)
            return self._create_validated_dataframe(structured_data)
        except Exception as e:
            logger.error(f"Data conversion failed: {str(e)}")
            raise

    def filter_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and remove anomalous records using AI pattern recognition.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame with anomaly report
        """
        data_sample = df.head().to_dict()
        prompt = f"""Analyze this data sample and provide filtering rules:
        {data_sample}
        
        Output format:
        {{
            "filters": [
                {{"column": "col1", "condition": ">", "value": 100}},
                ...
            ],
            "confidence_threshold": 0.95
        }}
        """
        
        try:
            response = self._get_ai_response(prompt)
            filters = response.get('filters', [])
            return self._apply_filters(df, filters)
        except Exception as e:
            logger.error(f"Anomaly filtering failed: {str(e)}")
            raise

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data using AI-suggested transformations.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Normalized DataFrame with transformation report
        """
        stats = df.describe().to_dict()
        prompt = f"""Suggest normalization methods based on data statistics:
        {stats}
        
        Output format:
        {{
            "transformations": [
                {{"column": "col1", "method": "log", "parameters": {{}}}},
                ...
            ]
        }}
        """
        
        try:
            response = self._get_ai_response(prompt)
            return self._apply_transformations(df, response.get('transformations', []))
        except Exception as e:
            logger.error(f"Data normalization failed: {str(e)}")
            raise

    def _get_ai_response(self, prompt: str) -> Dict:
        """Execute AI request with standardized formatting"""
        request = ChatRequest(
            model=self.client.model,
            messages=[
                ChatMessage(
                    role="system",
                    content="You are a senior data engineer. Provide structured JSON responses."
                ),
                ChatMessage(role="user", content=prompt)
            ]
        )
        response = self.client.chat_completion(request)
        return self._validate_ai_output(response['content'])

    def _validate_ai_output(self, raw_response: str) -> Dict:
        """Parse and validate AI response structure"""
        # Implement JSON validation with error recovery
        # ... (actual implementation would use json.loads and schema validation)
        return {"columns": ["example"], "data": [{"example": "data"}]}

    def _create_validated_dataframe(self, structured_data: Dict) -> pd.DataFrame:
        """Create validated DataFrame using Pydantic models"""
        validated_data = [
            DataFrameRow(**row).model_dump()
            for row in structured_data.get('data', [])
        ]
        return pd.DataFrame(validated_data)

    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict]) -> pd.DataFrame:
        """Apply AI-generated filters to DataFrame"""
        for filter_def in filters:
            try:
                column = filter_def['column']
                condition = filter_def['condition']
                value = filter_def['value']
                
                if condition == ">":
                    df = df[df[column] > value]
                elif condition == "<":
                    df = df[df[column] < value]
                elif condition == "==":
                    df = df[df[column] == value]
                elif condition == "contains":
                    df = df[df[column].str.contains(value, na=False)]
                elif condition == "between":
                    df = df[df[column].between(value['low'], value['high'])]
                else:
                    logger.warning(f"Unsupported filter condition: {condition}")
                    
                logger.info(f"Applied filter: {column} {condition} {value}")
                
            except KeyError as e:
                logger.error(f"Invalid filter definition: {filter_def} - missing {str(e)}")
            except Exception as e:
                logger.error(f"Failed to apply filter {filter_def}: {str(e)}")
                raise
                
        return df

    def _apply_transformations(self, df: pd.DataFrame, transformations: List[Dict]) -> pd.DataFrame:
        """Apply AI-suggested normalization methods"""
        import numpy as np
        
        for transform in transformations:
            try:
                col = transform['column']
                method = transform['method']
                params = transform.get('parameters', {})
                
                if method == "log":
                    df[col] = np.log(df[col] + params.get('epsilon', 1e-6))
                elif method == "zscore":
                    mean = df[col].mean()
                    std = df[col].std()
                    df[col] = (df[col] - mean) / std
                elif method == "minmax":
                    min_val = df[col].min()
                    max_val = df[col].max()
                    df[col] = (df[col] - min_val) / (max_val - min_val)
                elif method == "bin":
                    bins = params.get('bins', 10)
                    df[col] = pd.cut(df[col], bins=bins)
                else:
                    logger.warning(f"Unsupported transformation: {method}")
                    
                logger.info(f"Applied {method} transformation to {col}")
                
            except KeyError as e:
                logger.error(f"Invalid transformation definition: {transform} - missing {str(e)}")
            except Exception as e:
                logger.error(f"Failed to apply {method} to {col}: {str(e)}")
                raise
                
        return df

    def validate_input_data(self, data: str) -> bool:
        """Basic validation before processing"""
        if not data.strip():
            raise ValueError("Input data cannot be empty")
        return True

    def add_step(self, step_name: str, config: Dict):
        """Add a processing step to the pipeline"""
        valid_steps = ['convert', 'filter', 'normalize', 'validate']
        if step_name not in valid_steps:
            raise ValueError(f"Invalid step '{step_name}'. Valid steps: {valid_steps}")
            
        self._processing_pipeline.append({
            'step': step_name,
            'config': config,
            'applied': False,
            'result': None
        })

    def execute_pipeline(self, raw_data: str) -> pd.DataFrame:
        """Execute all steps in the pipeline sequentially"""
        if not self._processing_pipeline:
            raise ValueError("No steps in processing pipeline")
            
        df = pd.DataFrame()
        execution_report = []
        
        for idx, step in enumerate(self._processing_pipeline):
            try:
                if step['step'] == 'convert':
                    df = self.convert_to_dataframe(raw_data)
                elif step['step'] == 'filter':
                    df = self.filter_anomalies(df)
                elif step['step'] == 'normalize':
                    df = self.normalize_data(df)
                elif step['step'] == 'validate':
                    self.validate_input_data(raw_data)
                
                self._processing_pipeline[idx]['applied'] = True
                self._processing_pipeline[idx]['result'] = "Success"
                execution_report.append(f"Step {idx+1}: {step['step']} - Success")
                
            except Exception as e:
                self._processing_pipeline[idx]['result'] = str(e)
                execution_report.append(f"Step {idx+1}: {step['step']} - Failed: {str(e)}")
                logger.error(f"Pipeline failed at step {idx+1} ({step['step']}): {str(e)}")
                raise
            
        logger.info("Pipeline execution completed:\n" + "\n".join(execution_report))
        return df

    def clear_pipeline(self):
        """Reset the processing pipeline"""
        self._processing_pipeline = []
