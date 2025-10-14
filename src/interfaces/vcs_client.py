"""
Protocol interface for Version Control System (VCS) clients.

This module defines the abstract interface for VCS operations,
following the Interface Segregation Principle (ISP).

Agents depend on this interface, not concrete implementations.
"""

from typing import Protocol, List, Dict, Any, Optional
from datetime import datetime


class IssueProtocol(Protocol):
    """Protocol for issue objects."""

    @property
    def number(self) -> int:
        """Issue number."""
        ...

    @property
    def title(self) -> str:
        """Issue title."""
        ...

    @property
    def body(self) -> str:
        """Issue body/description."""
        ...

    @property
    def state(self) -> str:
        """Issue state (open, closed, etc.)."""
        ...

    @property
    def labels(self) -> List[str]:
        """Issue labels."""
        ...

    @property
    def created_at(self) -> datetime:
        """When the issue was created."""
        ...


class PullRequestProtocol(Protocol):
    """Protocol for pull request objects."""

    @property
    def number(self) -> int:
        """PR number."""
        ...

    @property
    def title(self) -> str:
        """PR title."""
        ...

    @property
    def body(self) -> str:
        """PR description."""
        ...

    @property
    def state(self) -> str:
        """PR state (open, closed, merged)."""
        ...

    @property
    def head_ref(self) -> str:
        """Source branch name."""
        ...

    @property
    def base_ref(self) -> str:
        """Target branch name."""
        ...


class VCSClientProtocol(Protocol):
    """
    Protocol defining VCS client interface.

    This interface defines the contract that all VCS clients must implement.
    Agents depend on this interface, allowing for easy mocking and testing.

    Follows Interface Segregation Principle - only essential methods included.
    """

    # ============================================
    # Issue Operations
    # ============================================

    def get_issue(self, issue_number: int) -> IssueProtocol:
        """
        Get issue by number.

        Args:
            issue_number: Issue number

        Returns:
            IssueProtocol: Issue object
        """
        ...

    def create_issue_comment(
        self,
        issue_number: int,
        comment_body: str
    ) -> None:
        """
        Add comment to an issue.

        Args:
            issue_number: Issue number
            comment_body: Comment text (Markdown supported)
        """
        ...

    def add_labels_to_issue(
        self,
        issue_number: int,
        labels: List[str]
    ) -> None:
        """
        Add labels to an issue.

        Args:
            issue_number: Issue number
            labels: List of label names
        """
        ...

    def remove_labels_from_issue(
        self,
        issue_number: int,
        labels: List[str]
    ) -> None:
        """
        Remove labels from an issue.

        Args:
            issue_number: Issue number
            labels: List of label names to remove
        """
        ...

    # ============================================
    # Pull Request Operations
    # ============================================

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> PullRequestProtocol:
        """
        Create a new pull request.

        Args:
            title: PR title
            body: PR description (Markdown)
            head_branch: Source branch name
            base_branch: Target branch name

        Returns:
            PullRequestProtocol: Created PR object
        """
        ...

    def get_pull_request(self, pr_number: int) -> PullRequestProtocol:
        """
        Get pull request by number.

        Args:
            pr_number: PR number

        Returns:
            PullRequestProtocol: PR object
        """
        ...

    def create_pr_comment(
        self,
        pr_number: int,
        comment_body: str
    ) -> None:
        """
        Add comment to a pull request.

        Args:
            pr_number: PR number
            comment_body: Comment text (Markdown supported)
        """
        ...

    def link_issue_to_pr(
        self,
        pr_number: int,
        issue_number: int
    ) -> None:
        """
        Link an issue to a pull request.

        Args:
            pr_number: PR number
            issue_number: Issue number to link
        """
        ...

    # ============================================
    # Branch Operations
    # ============================================

    def create_branch(
        self,
        branch_name: str,
        from_branch: str = "main"
    ) -> None:
        """
        Create a new branch.

        Args:
            branch_name: Name for the new branch
            from_branch: Base branch to create from
        """
        ...

    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if a branch exists.

        Args:
            branch_name: Branch name to check

        Returns:
            bool: True if branch exists
        """
        ...

    # ============================================
    # File Operations
    # ============================================

    def create_or_update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str
    ) -> None:
        """
        Create or update a file in the repository.

        Args:
            file_path: Path to the file
            content: File content
            commit_message: Commit message
            branch: Branch name
        """
        ...

    def get_file_content(
        self,
        file_path: str,
        branch: str = "main"
    ) -> Optional[str]:
        """
        Get file content from repository.

        Args:
            file_path: Path to the file
            branch: Branch name

        Returns:
            Optional[str]: File content or None if not found
        """
        ...

    def delete_file(
        self,
        file_path: str,
        commit_message: str,
        branch: str
    ) -> None:
        """
        Delete a file from the repository.

        Args:
            file_path: Path to the file
            commit_message: Commit message
            branch: Branch name
        """
        ...

    # ============================================
    # Repository Information
    # ============================================

    def get_repository_structure(
        self,
        path: str = "",
        branch: str = "main"
    ) -> List[Dict[str, Any]]:
        """
        Get repository file structure.

        Args:
            path: Directory path (empty for root)
            branch: Branch name

        Returns:
            List[Dict[str, Any]]: List of files and directories
        """
        ...
