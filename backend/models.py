from pydantic import BaseModel

class ReadmeRequest(BaseModel):
    folder_path: str

class ReadmeResponse(BaseModel):
    readme_markdown: str
    installation_steps: list[str]
    badges: list[str]
    architecture_overview: str
    contribution_guidelines: str
    license_suggestion: str
