import os
from typing import Optional
from pydantic_settings import BaseSettings


class FediversoSettings(BaseSettings):
    """Configuración de la extensión Fediverso."""

    # Configuración general
    extension_name: str = "fediverso"
    debug: bool = False

    # Configuración de base de datos
    database_url: Optional[str] = None

    # Configuración de OAuth2 para Mastodon
    mastodon_client_id: Optional[str] = None
    mastodon_client_secret: Optional[str] = None
    mastodon_redirect_uri: Optional[str] = None

    # Configuración de API
    api_timeout: int = 30
    max_retries: int = 3

    class Config:
        env_prefix = "FEDIVERSO_"
        case_sensitive = False


settings = FediversoSettings()
