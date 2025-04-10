# external imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# internal imports  
from modules.authentication import authentication_router
from core.config import settings
from modules.integration import integration_router
from modules.integration.routes import hubspot_router
from modules.projects import projects_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# Initialize the FastAPI application
app = FastAPI(
    title="Akkizon API",
    description="API for Akkizon application",
    version="0.1.0",
    contact={
        "name": "Meet Ai Coders",
    },
    lifespan=lifespan,
)

# Include your router
# app.include_router(data_processor_router)   
app.include_router(authentication_router)
app.include_router(integration_router)
app.include_router(hubspot_router)
app.include_router(projects_router)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.akkizon.ai", "http://localhost:3000", "https://akkizon-ui.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app)
