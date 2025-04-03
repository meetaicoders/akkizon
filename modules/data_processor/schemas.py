from pydantic import BaseModel, field_validator, Field
from uuid import UUID
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

class AddProjectRequest(BaseModel):
    name: Optional[str] = None
    project_id: Optional[str] = None

    @field_validator('project_id')
    def validate_project_id(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v
    
class FetchProjectByIdRequest(BaseModel):
    project_id: str

    @field_validator('project_id')
    def validate_project_id(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v

class HubSpotConfigSchema(BaseModel):
    scopes: List[str] = Field(
        default=[
            "content", "oauth", "crm.lists.read", "crm.objects.contacts.read", 
            "crm.objects.contacts.write", "crm.objects.custom.read", 
            "crm.objects.custom.write", "crm.objects.companies.write", 
            "crm.schemas.contacts.read", "crm.lists.write", 
            "crm.objects.companies.read", "crm.objects.deals.read", 
            "crm.objects.deals.write", "crm.schemas.companies.read", 
            "crm.schemas.companies.write", "crm.schemas.contacts.write", 
            "crm.schemas.deals.read", "crm.schemas.deals.write", 
            "crm.objects.owners.read", "crm.objects.goals.read", 
            "crm.objects.line_items.read", "crm.objects.line_items.write", 
            "crm.objects.marketing_events.read", "crm.objects.marketing_events.write", 
            "crm.objects.quotes.read", "crm.objects.quotes.write", 
            "crm.schemas.custom.read", "crm.schemas.line_items.read", 
            "crm.schemas.quotes.read", "tickets"
        ],
        description="List of OAuth scopes required for HubSpot integration"
    )

class FileUploadConfigSchema(BaseModel):
    supported_file_types: List[str] = Field(
        default=["CSV", "Excel", "JSON"],
        description="List of supported file types for file upload"
    )

class HubSpotConnectorSchema(BaseModel):
    auth_type: str = Field(default="oauth", description="Authentication type for HubSpot")
    config_schema: HubSpotConfigSchema = Field(description="Configuration schema for HubSpot")
    connector_type: str = Field(default="hubspot", description="Type of connector")

class FileUploadConnectorSchema(BaseModel):
    auth_type: str = Field(default="file_upload", description="Authentication type for file upload")
    config_schema: FileUploadConfigSchema = Field(description="Configuration schema for file upload")
    connector_type: str = Field(default="file_upload", description="Type of connector")

class HubSpotOAuthToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int
    user_id: str
    organization_id: str
    project_id: str
    connector_id: str