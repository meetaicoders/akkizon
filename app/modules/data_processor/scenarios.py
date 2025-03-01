# import logging
# import pandas as pd
# from pathlib import Path
# from typing import Optional, Dict, Any
# from pydantic import BaseModel
# from app.modules.data_processor.services import DataPreProcessor

# logger = logging.getLogger(__name__)

# class DataProcessingStep(BaseModel):
#     operation: str
#     parameters: Dict[str, Any]
#     status: str = "pending"
#     result: Optional[Dict] = None
#     error: Optional[str] = None

# class DataProcessingResult:
#     def __init__(self):
#         self.steps = []
#         self.current_df = None
#         self.error = None
        
#     def add_step(self, step: DataProcessingStep):
#         self.steps.append(step)
        
#     def get_report(self) -> Dict:
#         return {
#             "success": all(step.status == "completed" for step in self.steps),
#             "steps_executed": len(self.steps),
#             "current_shape": self.current_df.shape if self.current_df is not None else None,
#             "errors": [step.error for step in self.steps if step.error]
#         }

# class DataProcessingScenario:
#     def __init__(self, processor: Optional[DataPreProcessor] = None, 
#                  halt_on_error: bool = True, auto_run: bool = True):
#         self.processor = processor or DataPreProcessor()
#         self.result = DataProcessingResult()
#         self.halt_on_error = halt_on_error
#         self.auto_run = auto_run
#         self._processing_steps = []

#     def convert_data(self, raw_data: str) -> "DataProcessingScenario":
#         """Chainable data conversion method"""
#         step = DataProcessingStep(
#             operation="convert",
#             parameters={"raw_data": raw_data}
#         )
#         self._processing_steps.append(step)
#         return self._execute_step(step) if self.auto_run else self

#     def filter_data(self, filter_config: Optional[Dict] = None) -> "DataProcessingScenario":
#         """Chainable data filtering method"""
#         step = DataProcessingStep(
#             operation="filter",
#             parameters={"config": filter_config or {}}
#         )
#         self._processing_steps.append(step)
#         return self._execute_step(step) if self.auto_run else self

#     def normalize_data(self, normalize_config: Optional[Dict] = None) -> "DataProcessingScenario":
#         """Chainable data normalization method"""
#         step = DataProcessingStep(
#             operation="normalize",
#             parameters={"config": normalize_config or {}}
#         )
#         self._processing_steps.append(step)
#         return self._execute_step(step) if self.auto_run else self

#     def validate_data(self, validation_rules: Dict) -> "DataProcessingScenario":
#         """Chainable data validation method"""
#         step = DataProcessingStep(
#             operation="validate",
#             parameters={"rules": validation_rules}
#         )
#         self._processing_steps.append(step)
#         return self._execute_step(step) if self.auto_run else self

#     def save_data(self, file_path: str, format: str = "csv") -> "DataProcessingScenario":
#         """Chainable data saving method"""
#         step = DataProcessingStep(
#             operation="save",
#             parameters={"path": file_path, "format": format}
#         )
#         self._processing_steps.append(step)
#         return self._execute_step(step) if self.auto_run else self

#     def _execute_step(self, step: DataProcessingStep) -> "DataProcessingScenario":
#         """Internal method to execute a single processing step"""
#         try:
#             if step.operation == "convert":
#                 self.result.current_df = self.processor.convert_to_dataframe(
#                     step.parameters["raw_data"]
#                 )
#                 step.result = {"columns": list(self.result.current_df.columns)}
                
#             elif step.operation == "filter" and self.result.current_df is not None:
#                 filtered_df = self.processor.filter_anomalies(
#                     self.result.current_df,
#                     **step.parameters["config"]
#                 )
#                 step.result = {
#                     "removed_records": len(self.result.current_df) - len(filtered_df)
#                 }
#                 self.result.current_df = filtered_df
                
#             elif step.operation == "normalize" and self.result.current_df is not None:
#                 normalized_df = self.processor.normalize_data(
#                     self.result.current_df,
#                     **step.parameters["config"]
#                 )
#                 step.result = {"transformations": len(normalized_df.columns)}
#                 self.result.current_df = normalized_df
                
#             elif step.operation == "validate" and self.result.current_df is not None:
#                 self.processor.validate_input_data(
#                     self.result.current_df.to_csv(index=False)
#                 )
#                 step.result = {"validated": True}
                
#             elif step.operation == "save" and self.result.current_df is not None:
#                 self._save_to_file(
#                     self.result.current_df,
#                     step.parameters["path"],
#                     step.parameters["format"]
#                 )
#                 step.result = {"path": step.parameters["path"]}
                
#             step.status = "completed"
            
#         except Exception as e:
#             step.status = "failed"
#             step.error = str(e)
#             logger.error(f"Step {step.operation} failed: {str(e)}")
#             if self.halt_on_error:
#                 raise
                
#         self.result.add_step(step)
#         return self

#     def run(self) -> DataProcessingResult:
#         """Execute all queued processing steps"""
#         if not self.auto_run:
#             for step in self._processing_steps:
#                 if step.status == "pending":
#                     self._execute_step(step)
#                 if self.halt_on_error and step.status == "failed":
#                     break
#         return self.result

#     def _save_to_file(self, df: pd.DataFrame, path: str, format: str):
#         """Save DataFrame to file with format validation"""
#         Path(path).parent.mkdir(parents=True, exist_ok=True)
        
#         if format == "csv":
#             df.to_csv(path, index=False)
#         elif format == "parquet":
#             df.to_parquet(path)
#         else:
#             raise ValueError(f"Unsupported format: {format}")
            
#     def get_current_state(self) -> Dict:
#         """Return current processing state snapshot"""
#         return {
#             "current_step": len(self.result.steps),
#             "data_shape": self.result.current_df.shape if self.result.current_df else None,
#             "errors": [s.error for s in self.result.steps if s.error]
#         }

#     def reset(self):
#         """Reset the scenario to initial state"""
#         self.result = DataProcessingResult()
#         self._processing_steps = [] 