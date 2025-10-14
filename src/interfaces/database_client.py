"""
Protocol interface for Database clients.

This module defines the abstract interface for database operations,
following the Interface Segregation Principle (ISP).

Agents depend on this interface, not concrete implementations.
"""

from typing import Protocol, List, Dict, Any, Optional
from datetime import datetime


class DatabaseClientProtocol(Protocol):
    """
    Protocol defining database client interface.

    This interface defines the contract that all database clients must implement.
    Agents depend on this interface for state management and logging.

    Follows Interface Segregation Principle - only essential methods included.
    """

    # ============================================
    # Conversation Management
    # ============================================

    def create_conversation(
        self,
        issue_id: int,
        issue_number: int,
        repo_full_name: str
    ) -> str:
        """
        Create a new conversation record.

        Args:
            issue_id: GitHub issue ID
            issue_number: GitHub issue number
            repo_full_name: Full repo name (owner/repo)

        Returns:
            str: Conversation UUID
        """
        ...

    def get_conversation(
        self,
        issue_number: int,
        repo_full_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation by issue number.

        Args:
            issue_number: GitHub issue number
            repo_full_name: Full repo name (owner/repo)

        Returns:
            Optional[Dict[str, Any]]: Conversation data or None
        """
        ...

    def update_conversation_status(
        self,
        conversation_id: str,
        status: str
    ) -> None:
        """
        Update conversation status.

        Args:
            conversation_id: Conversation UUID
            status: New status (analyzing, needs_clarification, ready_for_dev)
        """
        ...

    def update_conversation_analysis(
        self,
        conversation_id: str,
        analysis: Dict[str, Any]
    ) -> None:
        """
        Update conversation analysis data.

        Args:
            conversation_id: Conversation UUID
            analysis: Analysis data (IssueAnalysis serialized)
        """
        ...

    # ============================================
    # Agent Action Logging
    # ============================================

    def log_agent_action(
        self,
        conversation_id: Optional[str],
        agent_type: str,
        action_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Log an agent action.

        Args:
            conversation_id: Optional conversation UUID
            agent_type: Type of agent (ProductOwner, Developer)
            action_type: Type of action performed
            payload: Action data

        Returns:
            str: Action log UUID
        """
        ...

    def get_agent_actions(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get agent actions for a conversation.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of actions to return

        Returns:
            List[Dict[str, Any]]: List of action records
        """
        ...

    # ============================================
    # Code Generation Tracking
    # ============================================

    def create_code_generation(
        self,
        conversation_id: str,
        pr_number: Optional[int],
        files_changed: Dict[str, Any],
        tests_generated: Dict[str, Any],
        status: str
    ) -> str:
        """
        Create a code generation record.

        Args:
            conversation_id: Conversation UUID
            pr_number: Optional PR number
            files_changed: Files that were changed
            tests_generated: Tests that were generated
            status: Generation status

        Returns:
            str: Code generation UUID
        """
        ...

    def update_code_generation_status(
        self,
        generation_id: str,
        status: str,
        pr_number: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update code generation status.

        Args:
            generation_id: Code generation UUID
            status: New status
            pr_number: Optional PR number
            error_message: Optional error message
        """
        ...

    def get_code_generation(
        self,
        generation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get code generation by ID.

        Args:
            generation_id: Code generation UUID

        Returns:
            Optional[Dict[str, Any]]: Generation data or None
        """
        ...

    # ============================================
    # Generic Query Operations
    # ============================================

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a record into a table.

        Args:
            table: Table name
            data: Data to insert

        Returns:
            Dict[str, Any]: Inserted record with generated fields
        """
        ...

    def update(
        self,
        table: str,
        record_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a record in a table.

        Args:
            table: Table name
            record_id: Record UUID
            data: Data to update

        Returns:
            Dict[str, Any]: Updated record
        """
        ...

    def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Select records from a table.

        Args:
            table: Table name
            filters: Optional filter conditions
            limit: Optional result limit
            order_by: Optional ordering column

        Returns:
            List[Dict[str, Any]]: List of matching records
        """
        ...

    def delete(
        self,
        table: str,
        record_id: str
    ) -> None:
        """
        Delete a record from a table.

        Args:
            table: Table name
            record_id: Record UUID
        """
        ...
