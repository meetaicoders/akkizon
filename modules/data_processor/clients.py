# External imports
import boto3
import os
import uuid
from typing import Dict, Any, List
from authlib.integrations.httpx_client import OAuth2Client, AsyncOAuth2Client
from urllib.parse import urlencode
import secrets
from datetime import datetime
from httpx import AsyncClient
from fastapi import HTTPException

# Internal imports
from modules.data_processor.models import Dataset, DatasetAddRequest, ProjectAddRequest
from modules.authentication.clients import BigDataOAuthClient
from modules.data_processor.schemas import (
    AddProjectRequest, 
    HubSpotConfigSchema, 
    FileUploadConfigSchema, 
    HubSpotOAuthToken
)
from utils.helper_funcs import get_supabase_client
from core.logger import setup_logger
from core.constants import DATASET_BUCKET_NAME
from core.config import settings
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

class ProjectClient:
    def __init__(self, table_name: str = "projects"):
        """
        Initialize the ProjectsClient.
        
        Args:   
            table_name: Name of the table in the database (default: "projects")
        """
        self.client = get_supabase_client()
        self.dataset_client = DatasetClient()
        self.table_name = table_name

    def add_project(self, project_id: str, project_name: str, user_id: str, organization_id: str) -> Any:
        """
        Add a new project to the database.
        
        Args:
            project_id: The ID of the project
            project_name: The name of the project
            user_id: The ID of the user
            organization_id: The ID of the organization
            
        Returns:
            The response from the database
        """
        try:
            if not project_id or not user_id or not organization_id:
                raise ValueError("Missing required fields")
            if not project_name:
                logger.info(f"Project name is not provided, generating random name")
                project_name = self._generate_random_name(user_id, organization_id)
            logger.info(f"Adding project: {project_name} for user: {user_id} and organization: {organization_id}")
            response = self.client.table(self.table_name).insert({
                "id": project_id,
                "name": project_name,
                "user_id": user_id,
                "organization_id": organization_id
            }).execute()

            return response.data
        except Exception as e:
            logger.error(f"Failed to add project: {str(e)}")
            raise e
        
    def fetch_all_projects_by_organization(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all projects from the database.
        """
        logger.info(f"Fetching all projects for user: {user_id}")
        if not user_id or not organization_id:
            logger.error("User ID and organization ID are required")
            raise ValueError("User ID and organization ID are required")
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).eq("organization_id", organization_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch projects: {str(e)}")
            raise e
        
    def fetch_project_by_id(self, project_id: str, user_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Fetch a project from the database by ID.
        """
        logger.info(f"Fetching project by ID: {project_id}")
        if not project_id or not user_id or not organization_id:
            logger.error("Project ID, user ID, and organization ID are required")
            raise ValueError("Project ID, user ID, and organization ID are required")
        try:
            response = self.client.table(self.table_name).select("*").eq("id", project_id).eq("user_id", user_id).eq("organization_id", organization_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch project: {str(e)}")
            raise e
        
    def _generate_random_name(self, user_id: str, organization_id: str) -> str:
        """
        Generate a random name for the project.
        """
        if not user_id or not organization_id:
            logger.error("User ID and organization ID are required")
            raise ValueError("User ID and organization ID are required")
        all_projects = self.fetch_all_projects_by_organization(user_id, organization_id)
        if not isinstance(all_projects, list):
            raise ValueError("Invalid return type from fetch_all_projects")
        
        return f"Untitled Project {len(all_projects) + 1}"

class ConnectorClient:
    def __init__(self, data_connector_table: str = "data_connectors", user_connector_table: str = "user_connectors"):
        self.client = get_supabase_client()
        self.data_connector_table  = data_connector_table
        self.user_connector_table = user_connector_table

    def fetch_default_connectors(self) -> List[Dict[str, Any]]:
        response = self.client.table(self.data_connector_table).select("*").execute()
        return response.data
    
    def fetch_all_connectors_for_user(self, user_id: str, organization_id: str, project_id: str) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.user_connector_table)
                .select("*")
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .eq("project_id", project_id)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch connectors: {str(e)}")
            raise e


class HubSpotConnector(BigDataOAuthClient):
    def __init__(self, connector_id: str, organization_id: str, user_id: str, project_id: str):
        super().__init__(
            client=get_supabase_client(),
            connector_id=connector_id, 
            organization_id=organization_id, 
            user_id=user_id, 
            project_id=project_id,
            client_id=settings.hubspot_client_id,
            client_secret=settings.hubspot_client_secret,
            redirect_uri=settings.hubspot_redirect_uri
        )

class FileUploadConnector(ConnectorClient):
    def __init__(self, config: FileUploadConfigSchema):
        self.config = config

    def upload_file(self, file_path: str):
        """
        Upload a file based on the supported file types.
        """
        # Implement file upload logic here
        pass

    def process_file(self, file_path: str):
        """
        Process the uploaded file.
        """
        # Implement file processing logic here
        pass