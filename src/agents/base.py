"""
Base Agent class for OSOrganicAI.

This module implements the abstract base agent using LangChain.
All specialized agents inherit from this class.

Design Patterns:
- Template Method Pattern: Defines workflow with extension points
- Dependency Injection: All dependencies injected via constructor
- Strategy Pattern: Pluggable LLM via LangChain interface

SOLID Principles:
- Single Responsibility: Only handles agent workflow
- Open/Closed: Extended via abstract methods, not modified
- Liskov Substitution: All agents maintain base contract
- Interface Segregation: Depends on thin interfaces (protocols)
- Dependency Inversion: Depends on abstractions (BaseChatModel, protocols)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler

from src.interfaces.vcs_client import VCSClientProtocol
from src.interfaces.database_client import DatabaseClientProtocol
from src.utils.logger import LoggerMixin, log_function_call


class BaseAgent(ABC, LoggerMixin):
    """
    Abstract base agent using LangChain.

    This class provides the foundation for all AI agents in the system.
    It implements the Template Method pattern, where the workflow is defined
    but specific steps are delegated to child classes.

    All child instances inherit this class and customize behavior via:
    - get_domain_context(): Add domain-specific context
    - get_system_prompt(): Define agent role and capabilities
    - Additional methods as needed

    Attributes:
        llm: LangChain LLM instance
        vcs_client: Version control system client
        db_client: Database client
        agent_name: Name of the agent (from class name)
    """

    def __init__(
        self,
        llm: BaseChatModel,
        vcs_client: VCSClientProtocol,
        db_client: DatabaseClientProtocol
    ):
        """
        Initialize the base agent.

        Args:
            llm: LangChain LLM instance (dependency injection)
            vcs_client: VCS client implementation
            db_client: Database client implementation

        Example:
            >>> from src.utils.llm_factory import create_default_llm
            >>> llm = create_default_llm()
            >>> agent = MyAgent(llm, github_client, supabase_client)
        """
        self.llm = llm
        self.vcs_client = vcs_client
        self.db_client = db_client
        self.agent_name = self.__class__.__name__

        self.logger.info(
            "Agent initialized",
            agent_name=self.agent_name
        )

    # ============================================
    # Extension Points (Template Method Pattern)
    # ============================================

    @abstractmethod
    def get_domain_context(self) -> str:
        """
        Get domain-specific context for this agent.

        This method MUST be overridden in child instances to provide
        domain-specific knowledge (e.g., e-commerce, fintech, etc.).

        Returns:
            str: Domain-specific context string

        Example (in child instance):
            >>> def get_domain_context(self) -> str:
            ...     return '''
            ...     E-commerce platform context:
            ...     - Consider inventory management
            ...     - Ensure PCI-DSS compliance
            ...     '''
        """
        return ""

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get system prompt defining agent's role and capabilities.

        This method MUST be overridden to define what the agent does.

        Returns:
            str: System prompt for the agent

        Example:
            >>> def get_system_prompt(self) -> str:
            ...     return "You are an expert Product Owner..."
        """
        pass

    def customize_prompt(self, base_prompt: str) -> str:
        """
        Customize prompt with additional instructions.

        Override this method to add extra prompt engineering.
        By default, returns the prompt unchanged.

        Args:
            base_prompt: Base prompt string

        Returns:
            str: Customized prompt
        """
        return base_prompt

    # ============================================
    # Core Agent Methods (Template Method)
    # ============================================

    def build_messages(
        self,
        user_input: str,
        conversation_history: Optional[List[BaseMessage]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> List[BaseMessage]:
        """
        Build LangChain messages for the LLM.

        This is the template method that constructs the full prompt
        by combining system prompt, domain context, and user input.

        Args:
            user_input: User's input or task description
            conversation_history: Optional previous messages
            additional_context: Optional additional context dict

        Returns:
            List[BaseMessage]: List of LangChain messages
        """
        # Get components
        domain_context = self.get_domain_context()
        system_prompt = self.get_system_prompt()

        # Build full system message
        full_system_prompt = f"{system_prompt}"

        if domain_context:
            full_system_prompt += f"\n\n## Domain Context\n{domain_context}"

        if additional_context:
            context_str = "\n".join(
                f"- {key}: {value}"
                for key, value in additional_context.items()
            )
            full_system_prompt += f"\n\n## Additional Context\n{context_str}"

        # Customize if needed
        full_system_prompt = self.customize_prompt(full_system_prompt)

        # Build messages
        messages: List[BaseMessage] = [
            SystemMessage(content=full_system_prompt)
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user input
        messages.append(HumanMessage(content=user_input))

        self.logger.debug(
            "Built messages for LLM",
            message_count=len(messages),
            has_history=bool(conversation_history),
            has_context=bool(additional_context)
        )

        return messages

    @log_function_call
    def invoke_llm(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> str:
        """
        Invoke the LLM with messages.

        This method handles LLM invocation with error handling and logging.

        Args:
            messages: List of LangChain messages
            **kwargs: Additional arguments for LLM

        Returns:
            str: LLM response content

        Raises:
            Exception: If LLM invocation fails
        """
        try:
            self.logger.info(
                "Invoking LLM",
                agent_name=self.agent_name,
                message_count=len(messages)
            )

            response = self.llm.invoke(messages, **kwargs)

            self.logger.info(
                "LLM invocation successful",
                agent_name=self.agent_name,
                response_length=len(response.content)
            )

            return response.content

        except Exception as e:
            self.logger.error(
                "LLM invocation failed",
                agent_name=self.agent_name,
                error=str(e),
                exc_info=True
            )
            raise

    def invoke_with_retry(
        self,
        messages: List[BaseMessage],
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Invoke LLM with retry logic.

        Args:
            messages: List of LangChain messages
            max_retries: Maximum number of retries
            **kwargs: Additional arguments for LLM

        Returns:
            str: LLM response content

        Raises:
            Exception: If all retries fail
        """
        from tenacity import retry, stop_after_attempt, wait_exponential

        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        def _invoke_with_retry():
            return self.invoke_llm(messages, **kwargs)

        return _invoke_with_retry()

    # ============================================
    # State Management & Logging
    # ============================================

    def log_action(
        self,
        action_type: str,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Log an agent action to the database.

        All child agents inherit this logging capability.

        Args:
            action_type: Type of action performed
            payload: Action data
            conversation_id: Optional conversation UUID

        Returns:
            str: Action log UUID
        """
        self.logger.info(
            "Logging agent action",
            agent_name=self.agent_name,
            action_type=action_type,
            conversation_id=conversation_id
        )

        return self.db_client.log_agent_action(
            conversation_id=conversation_id,
            agent_type=self.agent_name,
            action_type=action_type,
            payload=payload
        )

    def update_conversation_state(
        self,
        conversation_id: str,
        status: str,
        analysis: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update conversation state in database.

        Args:
            conversation_id: Conversation UUID
            status: New status
            analysis: Optional analysis data
        """
        self.logger.info(
            "Updating conversation state",
            conversation_id=conversation_id,
            status=status
        )

        self.db_client.update_conversation_status(conversation_id, status)

        if analysis:
            self.db_client.update_conversation_analysis(conversation_id, analysis)

    # ============================================
    # Helper Methods
    # ============================================

    def get_or_create_conversation(
        self,
        issue_number: int,
        issue_id: int,
        repo_full_name: str
    ) -> str:
        """
        Get existing conversation or create new one.

        Args:
            issue_number: GitHub issue number
            issue_id: GitHub issue ID
            repo_full_name: Full repo name (owner/repo)

        Returns:
            str: Conversation UUID
        """
        # Try to get existing conversation
        conversation = self.db_client.get_conversation(
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        if conversation:
            self.logger.info(
                "Found existing conversation",
                conversation_id=conversation["id"],
                issue_number=issue_number
            )
            return conversation["id"]

        # Create new conversation
        self.logger.info(
            "Creating new conversation",
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        conversation_id = self.db_client.create_conversation(
            issue_id=issue_id,
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        return conversation_id

    def format_github_comment(
        self,
        content: str,
        include_signature: bool = True
    ) -> str:
        """
        Format content for GitHub comment with agent signature.

        Args:
            content: Comment content (Markdown)
            include_signature: Whether to include agent signature

        Returns:
            str: Formatted comment
        """
        formatted = content

        if include_signature:
            formatted += f"\n\n---\n*{self.agent_name} 🤖*"

        return formatted

    @property
    def agent_version(self) -> str:
        """Get agent version (for tracking template updates)."""
        return getattr(self, "_agent_version", "1.0.0")

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.agent_name}(llm={self.llm.__class__.__name__})"
