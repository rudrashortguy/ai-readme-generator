import httpx, json
from config import settings

OLLAMA_URL = f"{settings.ollama_base_url}/api/generate"

SYSTEM_PROMPT = """You generate professional README files from project scans. Return strict JSON:
{
  "readme_markdown": "# Project Title\\n...",
  "installation_steps": ["Step 1", "Step 2"],
  "badges": ["![Python](https://img.shields.io/badge/Python-3.12-blue)"],
  "architecture_overview": "Mermaid diagram code",
  "contribution_guidelines": "...",
  "license_suggestion": "MIT"
}"""

async def query_ollama(tree: str, tech_stack: str, entry_snippet: str) -> dict:
    prompt = f"Directory tree:\n{tree}\n\nTech stack: {tech_stack}\n\nEntry file snippet:\n{entry_snippet}"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.2},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        return json.loads(resp.json()["response"])
