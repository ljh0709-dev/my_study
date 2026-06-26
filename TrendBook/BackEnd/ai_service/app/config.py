import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / '.env')


@dataclass(frozen=True)
class Settings:
    service_name: str = 'trendbook-ai'
    environment: str = os.getenv('APP_ENV', 'local')
    internal_ai_secret: str = os.getenv(
        'INTERNAL_AI_SECRET',
        'local-development-secret',
    )
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_base_url: str = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-5.4-mini')
    openai_embedding_model: str = os.getenv(
        'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small',
    )
    openai_embedding_dimensions: int = int(os.getenv('OPENAI_EMBEDDING_DIMENSIONS', '768'))
    openai_timeout_seconds: float = float(os.getenv('OPENAI_TIMEOUT_SECONDS', '60'))


settings = Settings()

