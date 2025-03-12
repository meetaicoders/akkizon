# External imports
import boto3
import os
import uuid
from typing import Dict, Any

# Internal imports
from data_processor.models import Dataset, DatasetAddRequest, ProjectAddRequest
from utils.helper_funcs import get_supabase_client
from core.logger import setup_logger
from core.constants import DATASET_BUCKET_NAME
logger = setup_logger(__name__)


class DatasetClient:
    """
    Client for uploading and managing datasets.
    Methods:
        - upload_to_bucket: Upload a file to the bucket using a UUID as the object name.
        - create_dataset_entry: Create a dataset in the database.
        - read_dataset_entry: Read a dataset from the database.
        - update_dataset_entry: Update a dataset in the database.
        - delete_dataset_entry: Delete a dataset from the database.
        - add_dataset: Add a dataset to the database.
    """
    def __init__(self, table_name: str = "datasets"):
        self.client = get_supabase_client()
        self.bucket_name = DATASET_BUCKET_NAME
        self.s3 = boto3.client("s3")
        self.table_name = table_name
    def upload_to_bucket(self, file: str) -> str:
        """
        Upload a file to the bucket using a UUID as the object name.
        """
        if not os.path.exists(file):
            raise FileNotFoundError(f"File {file} not found")
        try:
            logger.debug(f"Starting dataset upload for file: {file}")
            # Generate a UUID for the file name
            dataset_id = str(uuid.uuid4())
            # Get the file extension
            file_extension = os.path.splitext(file)[1]
            # Create the new file name with UUID
            new_file_name = f"{dataset_id}{file_extension}"
            
            # Upload with the new file name
            self.s3.upload_file(file, self.bucket_name, new_file_name)
            logger.info(f"Uploaded {file} \nID: {dataset_id}")
            return dataset_id   
         
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise
        
    def create_dataset_entry(self, dataset_id: str, name: str, description: str) -> Dataset:
        """
        Create a dataset in the database.
        """
        response = (
            self.client.table(self.table_name)
            .insert({"dataset_id": dataset_id, "name": name, "description": description})
            .execute()
        )
        logger.info(f"Dataset processed successfully!")
        return response.data
    
    def read_dataset_entry(self, dataset_id: str) -> Dataset:
        """
        Read a dataset from the database.
        """
        response = (
            self.client.table(self.table_name)
            .select("*")\
            .eq("dataset_id", dataset_id)
            .execute()
        )
        return response.data[0]

    def update_dataset_entry(self, dataset_id: str, name: str, description: str) -> Dataset:
        """
        Update a dataset in the database.
        """
        response = (
            self.client.table(self.table_name)
            .update({"name": name, "description": description})
            .eq("dataset_id", dataset_id)
            .execute()
        )
        return response.data
    
    def delete_dataset_entry(self, dataset_id: str) -> Dataset:
        """
        Delete a dataset from the database.
        """
        response = (
            self.client.table(self.table_name)
            .delete(returning="representation")
            .eq("dataset_id", dataset_id)
            .execute()
        )
        return response.data
    
    def add_dataset(self, request: DatasetAddRequest) -> Dataset:
        """
        Add a dataset to the database.
        """
        dataset_id = self.upload_to_bucket(request.file)
        if not dataset_id:
            raise ValueError("Failed to upload dataset to bucket")
        response = self.create_dataset_entry(dataset_id, request.name, request.description)
        if not response:
            raise ValueError("Failed to create dataset entry in database")
        return response[0]

class ProjectsClient:
    def __init__(self, table_name: str = "projects"):
        """
        Initialize the ProjectsClient.
        
        Args:   
            table_name: Name of the table in the database (default: "projects")
        """
        self.client = get_supabase_client()
        self.dataset_client = DatasetClient()
        self.table_name = table_name

    def add_project(self, project_request: ProjectAddRequest) -> Dict[str, Any]:
        """
        Add a new project with its associated dataset.
        
        Args:
            project_request: ProjectAddRequest containing the project data
            
        Returns:
            Dictionary containing both project and dataset information
        """
        try:
            # First add the dataset
            dataset_result = self.dataset_client.add_dataset(project_request.dataset_upload)
            if not dataset_result or 'dataset_id' not in dataset_result:
                raise ValueError("Failed to add dataset")
            
            input_data = {
                "dataset_id": dataset_result['dataset_id'],
                "name": project_request.name,
                "description": project_request.description
            }
            # Then create the project
            response = (
                self.client.table(self.table_name)
                .insert(input_data)
                .execute()
            )
            
            return {
                "project": response.data[0],
                "dataset": dataset_result
            }
            
        except Exception as e:
            # Clean up if project creation fails
            if 'dataset_id' in locals():
                self.dataset_client.delete_dataset_entry(dataset_result['dataset_id'])
            raise e