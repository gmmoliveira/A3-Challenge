# A3 Code Challenge

- **Author:** Guilherme Oliveira
- **Date:** Aug-$20^{th}$-2025
- **Contact**: gmmoliveira1@gmail.com / +55 (31) 9 8889 4273

# Incident Information Extraction API

This project implements a Python API that processes incident descriptions using a local LLM (Language Model) to extract structured information in JSON format.

## Systems Specifications

The source-code has been tested using the following systems:

- Python 3.13.5
- Ollama 0.11.4
- Nvidia RTX 4090 24GB VRAM GPU (recommended) or sufficient system RAM:
  - Driver Version: 575.64.03
  - CUDA Version: 12.9
- Ubuntu 22.04

## Installation

1. **Install Ollama**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

2. **Download LLM Model**:
```bash
ollama pull qwen3:32b
```

You can use a smaller model like `qwen3:0.6b` if you have limited resources. Note that changing to weaker base LLMs could lead to issues not limited to the textual quality but also including the formation of the final output json describing the incidents. Despite existing post-processing JSON enforcing code, this could lead to an error status provided by the `POST /extract_incident` endpoint i.e., the code will not crash, but an error message will be delivered back to the user.

1. **Set up Python Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. **Start the API Server**:
```bash
uvicorn src.agentic.endpoint:app --host 0.0.0.0 --port 8000
```

2. **Test the API**:
Run the Jupyter notebook at `src/visualization/main.ipynb` to test the endpoint with sample incident descriptions.

## API Endpoints

- `GET /health` - Service health check
- `POST /extract_incident` - Process incident description and return structured data

Example request:
```bash
curl -X POST "http://localhost:8000/extract_incident" \
-H "Content-Type: application/json" \
-d '{"base_text": "Ontem às 14h, no escritório de São Paulo, houve uma falha no servidor principal"}'
```

The provided example request leads to the following reply:

```json
{
    "status": "success",
    "message": {
        "data_ocorrencia": "2025-08-19 14:00",
        "local": "São Paulo",
        "tipo_incidente": "Falha no servidor",
        "impacto": null
    }
}
```

## Project Structure

```
├── src/agentic/
│   ├── endpoint.py          # FastAPI endpoints
│   └── agentic_workflow.py  # LLM processing logic
├── assets/endpoint_test_cases/
│   └── tests.json           # Test cases
└── src/visualization/
    └── main.ipynb           # Example usage and testing cases
```
