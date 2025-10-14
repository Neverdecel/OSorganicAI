"""
Supabase client wrapper for OSOrganicAI.

This module provides a type-safe wrapper around the Supabase client,
implementing the DatabaseClientProtocol interface.

Follows SOLID principles:
- Single Responsibility: Only handles database operations
- Open/Closed: Extended via composition, not modification
- Liskov Substitution: Implements DatabaseClientProtocol
- Interface Segregation: Thin, focused interface
- Dependency Inversion: Depends on Supabase abstraction
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from supabase import create_client, Client
from postgrest.exceptions import APIError

from src.interfaces.database_client import DatabaseClientProtocol
from src.utils.logger import get_logger, log_database_operation, RequestLogger


logger = get_logger(__name__)


class SupabaseClient(DatabaseClientProtocol):
    """
    Supabase client implementing DatabaseClientProtocol.

    This class wraps the Supabase Python client and provides
    type-safe methods for all database operations.

    Attributes:
        client: Supabase client instance
        url: Supabase project URL
    """

    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL
            key: Supabase API key (anon or service role)

        Example:
            >>> client = SupabaseClient(
            ...     url="https://xxx.supabase.co",
            ...     key="your-key"
            ... )
        """
        self.url = url
        self.client: Client = create_client(url, key)

        logger.info(
            "Supabase client initialized",
            url=url
        )

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

        Raises:
            Exception: If creation fails
        """
        with RequestLogger("create_conversation", issue_number=issue_number):
            try:
                data = {
                    "issue_id": issue_id,
                    "issue_number": issue_number,
                    "repo_full_name": repo_full_name,
                    "status": "analyzing",
                    "turns": [],
                }

                response = self.client.table("conversations").insert(data).execute()

                if not response.data:
                    raise Exception("Failed to create conversation: No data returned")

                conversation_id = response.data[0]["id"]

                log_database_operation(
                    operation="insert",
                    table="conversations",
                    conversation_id=conversation_id
                )

                return conversation_id

            except APIError as e:
                logger.error(
                    "Failed to create conversation",
                    error=str(e),
                    issue_number=issue_number,
                    exc_info=True
                )
                raise

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
        try:
            response = (
                self.client.table("conversations")
                .select("*")
                .eq("issue_number", issue_number)
                .eq("repo_full_name", repo_full_name)
                .execute()
            )

            if response.data and len(response.data) > 0:
                log_database_operation(
                    operation="select",
                    table="conversations",
                    found=True
                )
                return response.data[0]

            log_database_operation(
                operation="select",
                table="conversations",
                found=False
            )
            return None

        except APIError as e:
            logger.error(
                "Failed to get conversation",
                error=str(e),
                issue_number=issue_number,
                exc_info=True
            )
            raise

    def update_conversation_status(
        self,
        conversation_id: str,
        status: str
    ) -> None:
        """
        Update conversation status.

        Args:
            conversation_id: Conversation UUID
            status: New status

        Raises:
            Exception: If update fails
        """
        try:
            response = (
                self.client.table("conversations")
                .update({"status": status})
                .eq("id", conversation_id)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to update conversation status")

            log_database_operation(
                operation="update",
                table="conversations",
                conversation_id=conversation_id,
                status=status
            )

        except APIError as e:
            logger.error(
                "Failed to update conversation status",
                error=str(e),
                conversation_id=conversation_id,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If update fails
        """
        try:
            response = (
                self.client.table("conversations")
                .update({"analysis": json.dumps(analysis)})
                .eq("id", conversation_id)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to update conversation analysis")

            log_database_operation(
                operation="update",
                table="conversations",
                conversation_id=conversation_id,
                field="analysis"
            )

        except APIError as e:
            logger.error(
                "Failed to update conversation analysis",
                error=str(e),
                conversation_id=conversation_id,
                exc_info=True
            )
            raise

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
            agent_type: Type of agent
            action_type: Type of action performed
            payload: Action data

        Returns:
            str: Action log UUID

        Raises:
            Exception: If logging fails
        """
        try:
            data = {
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "action_type": action_type,
                "payload": json.dumps(payload),
                "status": "success",
            }

            response = self.client.table("agent_actions").insert(data).execute()

            if not response.data:
                raise Exception("Failed to log agent action")

            action_id = response.data[0]["id"]

            logger.debug(
                "Agent action logged",
                action_id=action_id,
                agent_type=agent_type,
                action_type=action_type
            )

            return action_id

        except APIError as e:
            logger.error(
                "Failed to log agent action",
                error=str(e),
                agent_type=agent_type,
                action_type=action_type,
                exc_info=True
            )
            raise

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
        try:
            response = (
                self.client.table("agent_actions")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data or []

        except APIError as e:
            logger.error(
                "Failed to get agent actions",
                error=str(e),
                conversation_id=conversation_id,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If creation fails
        """
        with RequestLogger("create_code_generation", conversation_id=conversation_id):
            try:
                data = {
                    "conversation_id": conversation_id,
                    "pr_number": pr_number,
                    "files_changed": json.dumps(files_changed),
                    "tests_generated": json.dumps(tests_generated),
                    "status": status,
                }

                response = self.client.table("code_generations").insert(data).execute()

                if not response.data:
                    raise Exception("Failed to create code generation record")

                generation_id = response.data[0]["id"]

                log_database_operation(
                    operation="insert",
                    table="code_generations",
                    generation_id=generation_id
                )

                return generation_id

            except APIError as e:
                logger.error(
                    "Failed to create code generation",
                    error=str(e),
                    conversation_id=conversation_id,
                    exc_info=True
                )
                raise

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

        Raises:
            Exception: If update fails
        """
        try:
            update_data = {"status": status}

            if pr_number is not None:
                update_data["pr_number"] = pr_number

            if error_message is not None:
                update_data["error_message"] = error_message

            response = (
                self.client.table("code_generations")
                .update(update_data)
                .eq("id", generation_id)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to update code generation status")

            log_database_operation(
                operation="update",
                table="code_generations",
                generation_id=generation_id,
                status=status
            )

        except APIError as e:
            logger.error(
                "Failed to update code generation status",
                error=str(e),
                generation_id=generation_id,
                exc_info=True
            )
            raise

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
        try:
            response = (
                self.client.table("code_generations")
                .select("*")
                .eq("id", generation_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None

        except APIError as e:
            logger.error(
                "Failed to get code generation",
                error=str(e),
                generation_id=generation_id,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If insert fails
        """
        try:
            response = self.client.table(table).insert(data).execute()

            if not response.data:
                raise Exception(f"Failed to insert into {table}")

            log_database_operation(operation="insert", table=table)

            return response.data[0]

        except APIError as e:
            logger.error(
                "Failed to insert record",
                error=str(e),
                table=table,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If update fails
        """
        try:
            response = (
                self.client.table(table)
                .update(data)
                .eq("id", record_id)
                .execute()
            )

            if not response.data:
                raise Exception(f"Failed to update {table}")

            log_database_operation(operation="update", table=table)

            return response.data[0]

        except APIError as e:
            logger.error(
                "Failed to update record",
                error=str(e),
                table=table,
                record_id=record_id,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If select fails
        """
        try:
            query = self.client.table(table).select("*")

            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            # Apply ordering
            if order_by:
                desc = order_by.startswith("-")
                column = order_by.lstrip("-")
                query = query.order(column, desc=desc)

            # Apply limit
            if limit:
                query = query.limit(limit)

            response = query.execute()

            log_database_operation(
                operation="select",
                table=table,
                result_count=len(response.data) if response.data else 0
            )

            return response.data or []

        except APIError as e:
            logger.error(
                "Failed to select records",
                error=str(e),
                table=table,
                exc_info=True
            )
            raise

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

        Raises:
            Exception: If delete fails
        """
        try:
            response = (
                self.client.table(table)
                .delete()
                .eq("id", record_id)
                .execute()
            )

            log_database_operation(operation="delete", table=table)

        except APIError as e:
            logger.error(
                "Failed to delete record",
                error=str(e),
                table=table,
                record_id=record_id,
                exc_info=True
            )
            raise


def create_supabase_client(url: str, key: str) -> SupabaseClient:
    """
    Factory function to create a Supabase client.

    Args:
        url: Supabase project URL
        key: Supabase API key

    Returns:
        SupabaseClient: Configured client instance

    Example:
        >>> client = create_supabase_client(
        ...     url=settings.supabase_url,
        ...     key=settings.supabase_service_role_key
        ... )
    """
    return SupabaseClient(url, key)


def create_supabase_client_from_settings(settings) -> SupabaseClient:
    """
    Create Supabase client from settings object.

    Args:
        settings: Settings instance

    Returns:
        SupabaseClient: Configured client instance

    Example:
        >>> from src.config.settings import get_settings
        >>> settings = get_settings()
        >>> client = create_supabase_client_from_settings(settings)
    """
    return create_supabase_client(
        url=settings.supabase_url,
        key=settings.supabase_service_role_key
    )
