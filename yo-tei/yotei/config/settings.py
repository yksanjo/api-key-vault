"""Configuration settings for Yo-tei."""

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


def get_config_dir() -> Path:
    """Get the config directory."""
    config_dir = Path.home() / ".yotei"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the config file path."""
    return get_config_dir() / "config.json"


class DeepSeekConfig(BaseModel):
    """DeepSeek API configuration."""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000


class RelayConfig(BaseModel):
    """Relay server configuration."""
    url: str = "ws://localhost:8765"
    reconnect_interval: int = 5  # seconds
    heartbeat_interval: int = 30  # seconds


class StripeConfig(BaseModel):
    """Stripe configuration for subscriptions."""
    api_key: str = ""
    price_id_pro: str = ""  # Monthly pro subscription price ID


class Settings(BaseModel):
    """Application settings."""

    # User identity (set during init)
    user_id: Optional[str] = None
    agent_id: Optional[str] = None

    # API configurations
    deepseek: DeepSeekConfig = Field(default_factory=DeepSeekConfig)
    relay: RelayConfig = Field(default_factory=RelayConfig)
    stripe: StripeConfig = Field(default_factory=StripeConfig)

    # App settings
    timezone: str = "America/Los_Angeles"
    notification_enabled: bool = True
    agent_auto_start: bool = True
    debug_mode: bool = False

    def save(self) -> None:
        """Save settings to config file."""
        config_path = get_config_path()
        with open(config_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file."""
        config_path = get_config_path()
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                return cls.model_validate(data)
        return cls()

    def is_configured(self) -> bool:
        """Check if essential settings are configured."""
        return bool(self.user_id and self.deepseek.api_key)

    def set_deepseek_key(self, api_key: str) -> None:
        """Set the DeepSeek API key."""
        self.deepseek.api_key = api_key
        self.save()

    def set_user(self, user_id: str, agent_id: str) -> None:
        """Set the current user."""
        self.user_id = user_id
        self.agent_id = agent_id
        self.save()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reset_settings() -> Settings:
    """Reset and reload settings."""
    global _settings
    _settings = Settings.load()
    return _settings


# Pre-configured DeepSeek API key (from user input)
DEFAULT_DEEPSEEK_KEY = "sk-23cf05610a7445df8016f6ac1e1f7ec7"


def initialize_with_defaults() -> Settings:
    """Initialize settings with default values."""
    settings = get_settings()
    if not settings.deepseek.api_key:
        settings.deepseek.api_key = DEFAULT_DEEPSEEK_KEY
        settings.save()
    return settings
