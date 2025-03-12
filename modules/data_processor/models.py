from pydantic import BaseModel, FilePath, field_validator
import uuid
from fastapi import UploadFile, File
from typing import Optional
import os

class Dataset(BaseModel):
    """
    A dataset is a collection of data that is used to train a model.
    """
    dataset_id: str
    name: str
    description: str
    created_at: str
    updated_at: str

class NewDatasetRequest(BaseModel):
    """
    A request to create a new dataset.
    """
    name: str
    description: str
    file: FilePath  # This ensures the file exists at the given path 

class DatasetAddRequest(BaseModel):
    """
    A request to add a new dataset.
    """
    name: str
    description: Optional[str] = None
    file: UploadFile

    @field_validator('file')
    def validate_file_type(cls, v):
        if v.filename:
            # Get the file extension
            ext = os.path.splitext(v.filename)[1].lower()
            # Check if the extension is allowed
            if ext not in ['.csv', '.xls', '.xlsx']:
                raise ValueError('File must be a CSV or Excel file')
        return v

class ProjectAddRequest(BaseModel):
    """
    A request to add a new project.
    """
    name: str
    description: Optional[str] = None
    dataset_upload: DatasetAddRequest