from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:latest"
    extract_dir: str = "temp_extracts"
    allowed_prefix: str = "/Users/rudra/Documents/projects-github/"
    cache_dir: str = "diskcache"

    model_config = {"env_prefix": "README_"}
settings = Settings()
