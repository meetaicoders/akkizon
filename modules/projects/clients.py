from typing import Any, Dict, List
from utils.helper_funcs import get_supabase_client
from core.logger import setup_logger

logger = setup_logger(__name__)

class ProjectClient:
    def __init__(self, table_name: str = "projects"):
        """
        Initialize the ProjectsClient.
        
        Args:   
            table_name: Name of the table in the database (default: "projects")
        """
        self.client = get_supabase_client()
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
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .execute()
            )
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
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("id", project_id)
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .execute()
            )
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