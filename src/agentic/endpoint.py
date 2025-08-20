from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from src.agentic.agentic_workflow import AgenticWorkflow, lifespan


# Creates an instance of the FastAPI application to host endpoints
app = FastAPI(lifespan=lifespan)


# Pydantic model for the endpoint input request structure
class RequestData(BaseModel):
    base_text: str


# Enables the endpoint to access the agentic workflow
def get_workflow(request: Request) -> AgenticWorkflow:
    """Dependency to get the workflow instance from app state"""
    if not hasattr(request.app.state, 'workflow') or not request.app.state.workflow_initialized:
        raise RuntimeError("AgenticWorkflow not initialized")
    return request.app.state.workflow


# Function which monitors input requests to the "/extract_incident" endpoint
@app.post("/extract_incident")
async def process_data(
    request: RequestData,
    workflow: AgenticWorkflow = Depends(get_workflow)
):
    """
    Process text data using the pre-initialized AgenticWorkflow instance.
    The workflow is instantiated only once during application startup.
    """
    result = await workflow.process_text(request.base_text)
    return result


# Function to verify the endpoints application is alive and healthy
@app.get("/health")
async def health_check():
    """Health check endpoint to verify the application is running"""
    return {
        "status": "healthy",
        "workflow_initialized": hasattr(app.state, 'workflow_initialized') and app.state.workflow_initialized
    }
