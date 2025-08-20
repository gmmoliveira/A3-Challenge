from agno.agent import Agent
from agno.models.ollama import Ollama
from ollama import AsyncClient
from textwrap import dedent
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field


class EndpointIncidentReportOutput(BaseModel):
    """Structured incident report extracted from textual descriptions"""
    
    data_ocorrencia: Optional[str] = Field(
        None,
        description="Date and time of incident occurrence in ISO 8601 format (YYYY-MM-DD HH:MM). Handle relative times like 'ontem' (yesterday) or 'há 2 horas' by calculating absolute datetime based on current context. Always use 24-hour format.",
        examples=[
            "2025-08-12 14:00",
            "2023-11-05 09:30",
            "2024-01-01 23:45",
            "2021-08-30",
        ]
    )
    
    local: Optional[str] = Field(
        None,
        description="Geographical location or physical facility where incident occurred. Extract city names, office references, or facility identifiers. Use canonical names when possible.",
        examples=[
            "São Paulo",
            "New York",
            "Datacenter Leste",
            "Escritório Principal"
        ]
    )
    
    tipo_incidente: Optional[str] = Field(
        None,
        description="Category classification of the incident. Use concise technical descriptions while maintaining original context from input text.",
        examples=[
            "Falha no servidor",
            "Service unavailable",
            "Corte de fibra ótica",
            "Interrupção de energia",
            "Erro de configuração"
        ]
    )
    
    impacto: Optional[str] = Field(
        None,
        description="Brief description of affected systems and duration. Preserve key details about scope and time impact while using concise language.",
        examples=[
            "Sistema de faturamento indisponível por 2 horas",
            "Latência aumentada em serviços web por 45 minutos",
            "Perda parcial de dados de monitoramento"
        ]
    )


class AgenticWorkflow:
    def __init__(
        self,
        port: int = 54256,
        temperature: float = 0.1,
        model_id: str = "qwen3:32b",
    ):
        assert port < (2 ** 16)
        assert 0.0 <= temperature <= 1.0
        self.async_client = AsyncClient(
            host=f"http://localhost:{port}",
            headers={
                "temperature": f"{temperature}"
            },
        )
        self.model = Ollama(
            id=model_id,
            async_client=self.async_client
        )
        self.agent = Agent(
            model=self.model,
            name="Incident Data Extractor",
            role="Specialized in extracting structured incident information from unstructured text",
            description="Expert at parsing incident reports to identify and extract key information including timestamps, locations, incident types, and impact descriptions with high accuracy",
            instructions=[
                "Carefully analyze the input text to identify all relevant incident information",
                "Extract date/time information and convert to standardized ISO format (YYYY-MM-DD HH:MM)",
                "Handle relative time references (e.g., 'ontem', 'há 2 horas') by calculating absolute timestamps",
                "Identify geographical locations, office names, or facility references for the 'local' field",
                "Classify incident types using consistent terminology from the provided examples",
                "Summarize impact descriptions concisely while preserving key details about affected systems and duration",
                "Maintain the original language of the input text in all output fields",
                "If information for a field is not present in the text, return null for that field",
                "Ensure all extracted information accurately reflects what is stated in the input text",
                "Ensure all extracted information accurately matched the language in the input text",
                "Output must strictly conform to the JSON schema defined by EndpointIncidentReportOutput",
            ],
            add_datetime_to_instructions=True,
            markdown=True,
            response_model=EndpointIncidentReportOutput,
            use_json_mode=True,
            success_criteria="Achieving JSON compliance with the defined response model structure",
        )

    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process text using the agent and return results"""
        try:
            result = self.agent.run(text)
            return {"status": "success", "message": result.content}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Lifespan context manager that handles startup and shutdown events.
    Initializes the AgenticWorkflow instance and stores it in app state.
    """
    # Startup logic
    print("Initializing AgenticWorkflow...")
    workflow = AgenticWorkflow()
    
    # Store in app state
    app.state.workflow = workflow
    app.state.workflow_initialized = True
    
    print("AgenticWorkflow is up and running")
    yield {"workflow": workflow}
    
    # Shutdown logic
    print("Shutting down AgenticWorkflow...")