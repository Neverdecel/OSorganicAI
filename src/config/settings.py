"""
Configuration management using Pydantic Settings.

This module provides type-safe configuration with validation at startup.
Follows the Single Responsibility Principle - only handles configuration.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings are loaded from environment variables with validation.
    Supports .env file loading for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================
    # AI Model Configuration
    # ============================================
    ai_model_provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai",
        description="AI model provider to use"
    )
    ai_api_key: str = Field(
        ...,
        description="API key for the AI provider"
    )
    ai_model_name: str = Field(
        default="gpt-4",
        description="Specific model name to use"
    )
    ai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for AI responses (0.0-2.0)"
    )
    ai_max_tokens: int = Field(
        default=2000,
        gt=0,
        le=100000,
        description="Maximum tokens for AI responses"
    )
    ai_timeout: int = Field(
        default=60,
        gt=0,
        description="Timeout in seconds for AI requests"
    )

    # ============================================
    # GitHub Configuration
    # ============================================
    github_token: str = Field(
        ...,
        description="GitHub Personal Access Token"
    )
    github_repo: str = Field(
        ...,
        description="GitHub repository (owner/repo format)"
    )
    github_webhook_secret: str = Field(
        ...,
        description="Secret for GitHub webhook verification"
    )
    github_api_timeout: int = Field(
        default=30,
        gt=0,
        description="Timeout for GitHub API requests"
    )

    # ============================================
    # Supabase Configuration
    # ============================================
    supabase_url: str = Field(
        ...,
        description="Supabase project URL"
    )
    supabase_anon_key: str = Field(
        ...,
        description="Supabase anonymous/public key"
    )
    supabase_service_role_key: str = Field(
        ...,
        description="Supabase service role key (private!)"
    )

    # ============================================
    # Application Configuration
    # ============================================
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    app_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="Port for local development"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # ============================================
    # Logging Configuration
    # ============================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format"
    )

    # ============================================
    # Vercel Configuration (Optional - set by Vercel)
    # ============================================
    vercel_env: Optional[str] = Field(
        default=None,
        description="Vercel environment (set automatically)"
    )
    vercel_url: Optional[str] = Field(
        default=None,
        description="Vercel deployment URL (set automatically)"
    )
    vercel_git_commit_sha: Optional[str] = Field(
        default=None,
        description="Git commit SHA (set by Vercel)"
    )

    # ============================================
    # Agent Configuration
    # ============================================
    agent_max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retries for agent operations"
    )
    agent_retry_delay: float = Field(
        default=1.0,
        ge=0.0,
        description="Delay between retries in seconds"
    )

    # ============================================
    # Validators
    # ============================================

    @field_validator("github_repo")
    @classmethod
    def validate_github_repo(cls, v: str) -> str:
        """Validate GitHub repo format (owner/repo)."""
        if "/" not in v:
            raise ValueError(
                "github_repo must be in 'owner/repo' format"
            )
        parts = v.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "github_repo must be in 'owner/repo' format with valid owner and repo names"
            )
        return v

    @field_validator("supabase_url")
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        """Validate Supabase URL format."""
        if not v.startswith("https://"):
            raise ValueError(
                "supabase_url must start with 'https://'"
            )
        if not v.endswith(".supabase.co"):
            raise ValueError(
                "supabase_url must be a valid Supabase URL ending with '.supabase.co'"
            )
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug_in_production(cls, v: bool, info) -> bool:
        """Warn if debug is enabled in production."""
        if v and info.data.get("app_env") == "production":
            import warnings
            warnings.warn(
                "Debug mode is enabled in production environment. "
                "This should only be used for troubleshooting.",
                UserWarning
            )
        return v

    # ============================================
    # Helper Methods
    # ============================================

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @property
    def is_vercel(self) -> bool:
        """Check if running on Vercel."""
        return self.vercel_env is not None

    def get_ai_model_config(self) -> dict:
        """Get AI model configuration as a dictionary."""
        return {
            "provider": self.ai_model_provider,
            "model": self.ai_model_name,
            "temperature": self.ai_temperature,
            "max_tokens": self.ai_max_tokens,
            "timeout": self.ai_timeout,
        }

    def get_github_config(self) -> dict:
        """Get GitHub configuration as a dictionary."""
        return {
            "token": self.github_token,
            "repo": self.github_repo,
            "webhook_secret": self.github_webhook_secret,
            "timeout": self.github_api_timeout,
        }

    def get_supabase_config(self) -> dict:
        """Get Supabase configuration as a dictionary."""
        return {
            "url": self.supabase_url,
            "anon_key": self.supabase_anon_key,
            "service_role_key": self.supabase_service_role_key,
        }


# Global settings instance (singleton pattern)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create global settings instance.

    This function implements a singleton pattern to ensure
    settings are loaded only once during application lifetime.

    Returns:
        Settings: Global settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Force reload settings from environment.

    Useful for testing or when environment variables change.

    Returns:
        Settings: Newly loaded settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
