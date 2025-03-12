# external imports
from fastapi import APIRouter, HTTPException

# internal imports
from core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/v1/data", tags=["data_processor"])