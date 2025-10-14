"""
LangChain LLM Factory for multi-provider support.

This module implements the Factory pattern to create LangChain LLM instances
for different AI providers (OpenAI, Anthropic, Ollama).

Follows SOLID principles:
- Single Responsibility: Only creates and configures LLM instances
- Open/Closed: Easy to extend with new providers
- Dependency Inversion: Returns abstract BaseChatModel interface
"""

from typing import Dict, Any, Optional
from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler

from src.utils.logger import get_logger, log_api_call


logger = get_logger(__name__)


class LLMCallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler for logging LLM interactions.

    Logs all LLM calls for debugging and monitoring purposes.
    """

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list[str],
        **kwargs: Any
    ) -> None:
        """Log when LLM starts processing."""
        logger.debug(
            "LLM call started",
            model=serialized.get("name", "unknown"),
            prompt_count=len(prompts)
        )

    def on_llm_end(
        self,
        response: Any,
        **kwargs: Any
    ) -> None:
        """Log when LLM completes processing."""
        logger.debug(
            "LLM call completed",
            response_type=type(response).__name__
        )

    def on_llm_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Log when LLM encounters an error."""
        logger.error(
            "LLM call failed",
            error_type=type(error).__name__,
            error_message=str(error),
            exc_info=True
        )


class LLMFactory:
    """
    Factory for creating LangChain LLM instances.

    Supports multiple AI providers with consistent interface.
    Implements the Factory pattern for flexibility and extensibility.
    """

    # Supported providers
    SUPPORTED_PROVIDERS = ["openai", "anthropic", "ollama"]

    # Default models for each provider
    DEFAULT_MODELS = {
        "openai": "gpt-4",
        "anthropic": "claude-3-opus-20240229",
        "ollama": "llama2"
    }

    # Model aliases for convenience
    MODEL_ALIASES = {
        "gpt4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo-preview",
        "gpt3.5": "gpt-3.5-turbo",
        "claude": "claude-3-opus-20240229",
        "claude-opus": "claude-3-opus-20240229",
        "claude-sonnet": "claude-3-sonnet-20240229",
        "claude-haiku": "claude-3-haiku-20240307",
    }

    @classmethod
    def create_llm(
        cls,
        provider: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: int = 60,
        streaming: bool = False,
        callbacks: Optional[list] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        Create a LangChain LLM instance for the specified provider.

        Args:
            provider: AI provider name ('openai', 'anthropic', 'ollama')
            model: Specific model name (uses default if not provided)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            api_key: API key for the provider
            timeout: Request timeout in seconds
            streaming: Whether to enable streaming responses
            callbacks: List of callback handlers
            **kwargs: Additional provider-specific parameters

        Returns:
            BaseChatModel: Configured LangChain LLM instance

        Raises:
            ValueError: If provider is not supported
            Exception: If LLM creation fails

        Example:
            >>> llm = LLMFactory.create_llm(
            ...     provider="openai",
            ...     model="gpt-4",
            ...     temperature=0.7
            ... )
        """
        # Normalize provider name
        provider = provider.lower().strip()

        # Validate provider
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Supported providers: {', '.join(cls.SUPPORTED_PROVIDERS)}"
            )

        # Use default model if not specified
        if model is None:
            model = cls.DEFAULT_MODELS[provider]
        else:
            # Resolve model aliases
            model = cls.MODEL_ALIASES.get(model, model)

        # Add logging callback if not present
        if callbacks is None:
            callbacks = []
        if not any(isinstance(cb, LLMCallbackHandler) for cb in callbacks):
            callbacks.append(LLMCallbackHandler())

        logger.info(
            "Creating LLM instance",
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        try:
            # Create LLM based on provider
            if provider == "openai":
                return cls._create_openai_llm(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                    timeout=timeout,
                    streaming=streaming,
                    callbacks=callbacks,
                    **kwargs
                )
            elif provider == "anthropic":
                return cls._create_anthropic_llm(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                    timeout=timeout,
                    streaming=streaming,
                    callbacks=callbacks,
                    **kwargs
                )
            elif provider == "ollama":
                return cls._create_ollama_llm(
                    model=model,
                    temperature=temperature,
                    callbacks=callbacks,
                    **kwargs
                )
            else:
                raise ValueError(f"Provider '{provider}' not implemented")

        except Exception as e:
            logger.error(
                "Failed to create LLM",
                provider=provider,
                model=model,
                error=str(e),
                exc_info=True
            )
            raise

    @staticmethod
    def _create_openai_llm(
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        api_key: Optional[str],
        timeout: int,
        streaming: bool,
        callbacks: list,
        **kwargs
    ) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        config = {
            "model_name": model,
            "temperature": temperature,
            "request_timeout": timeout,
            "streaming": streaming,
            "callbacks": callbacks,
        }

        if api_key:
            config["openai_api_key"] = api_key

        if max_tokens:
            config["max_tokens"] = max_tokens

        # Add any additional kwargs
        config.update(kwargs)

        return ChatOpenAI(**config)

    @staticmethod
    def _create_anthropic_llm(
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        api_key: Optional[str],
        timeout: int,
        streaming: bool,
        callbacks: list,
        **kwargs
    ) -> ChatAnthropic:
        """Create Anthropic LLM instance."""
        config = {
            "model": model,
            "temperature": temperature,
            "timeout": timeout,
            "streaming": streaming,
            "callbacks": callbacks,
        }

        if api_key:
            config["anthropic_api_key"] = api_key

        if max_tokens:
            config["max_tokens"] = max_tokens

        # Add any additional kwargs
        config.update(kwargs)

        return ChatAnthropic(**config)

    @staticmethod
    def _create_ollama_llm(
        model: str,
        temperature: float,
        callbacks: list,
        **kwargs
    ) -> ChatOllama:
        """Create Ollama LLM instance (local models)."""
        config = {
            "model": model,
            "temperature": temperature,
            "callbacks": callbacks,
        }

        # Add any additional kwargs (e.g., base_url for custom Ollama server)
        config.update(kwargs)

        return ChatOllama(**config)

    @classmethod
    def from_settings(
        cls,
        settings,
        callbacks: Optional[list] = None
    ) -> BaseChatModel:
        """
        Create LLM instance from application settings.

        Convenient method to create LLM from Settings object.

        Args:
            settings: Settings instance with AI configuration
            callbacks: Optional list of callback handlers

        Returns:
            BaseChatModel: Configured LLM instance

        Example:
            >>> from src.config.settings import get_settings
            >>> settings = get_settings()
            >>> llm = LLMFactory.from_settings(settings)
        """
        return cls.create_llm(
            provider=settings.ai_model_provider,
            model=settings.ai_model_name,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            api_key=settings.ai_api_key,
            timeout=settings.ai_timeout,
            callbacks=callbacks
        )

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported AI providers."""
        return cls.SUPPORTED_PROVIDERS.copy()

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """
        Get default model for a provider.

        Args:
            provider: Provider name

        Returns:
            str: Default model name

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        return cls.DEFAULT_MODELS[provider]


# Convenience function for common use case
def create_default_llm() -> BaseChatModel:
    """
    Create LLM instance with default settings from environment.

    Returns:
        BaseChatModel: Configured LLM instance

    Example:
        >>> llm = create_default_llm()
    """
    from src.config.settings import get_settings

    settings = get_settings()
    return LLMFactory.from_settings(settings)
