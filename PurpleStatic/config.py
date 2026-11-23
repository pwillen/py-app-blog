from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class AppSettings(BaseSettings, env_file=PROJECT_ROOT / ".env", extra="ignore", case_sensitive=False):
    tmdb_read_only_access_token: SecretStr

app_settings = AppSettings()