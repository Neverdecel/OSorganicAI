"""
GitHub API client wrapper for OSOrganicAI.

This module provides a type-safe wrapper around PyGithub,
implementing the VCSClientProtocol interface.

Follows SOLID principles:
- Single Responsibility: Only handles GitHub operations
- Open/Closed: Extended via composition, not modification
- Liskov Substitution: Implements VCSClientProtocol
- Interface Segregation: Thin, focused interface
- Dependency Inversion: Depends on GitHub abstraction
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.ContentFile import ContentFile

from src.interfaces.vcs_client import (
    VCSClientProtocol,
    IssueProtocol,
    PullRequestProtocol
)
from src.utils.logger import get_logger, log_api_call, RequestLogger


logger = get_logger(__name__)


class GitHubIssueWrapper:
    """
    Wrapper for GitHub Issue to implement IssueProtocol.

    This adapter makes PyGithub's Issue compatible with our protocol.
    """

    def __init__(self, issue: Issue):
        self._issue = issue

    @property
    def number(self) -> int:
        return self._issue.number

    @property
    def title(self) -> str:
        return self._issue.title

    @property
    def body(self) -> str:
        return self._issue.body or ""

    @property
    def state(self) -> str:
        return self._issue.state

    @property
    def labels(self) -> List[str]:
        return [label.name for label in self._issue.labels]

    @property
    def created_at(self) -> datetime:
        return self._issue.created_at


class GitHubPullRequestWrapper:
    """
    Wrapper for GitHub PullRequest to implement PullRequestProtocol.

    This adapter makes PyGithub's PullRequest compatible with our protocol.
    """

    def __init__(self, pr: PullRequest):
        self._pr = pr

    @property
    def number(self) -> int:
        return self._pr.number

    @property
    def title(self) -> str:
        return self._pr.title

    @property
    def body(self) -> str:
        return self._pr.body or ""

    @property
    def state(self) -> str:
        return self._pr.state

    @property
    def head_ref(self) -> str:
        return self._pr.head.ref

    @property
    def base_ref(self) -> str:
        return self._pr.base.ref


class GitHubClient(VCSClientProtocol):
    """
    GitHub client implementing VCSClientProtocol.

    This class wraps PyGithub and provides type-safe methods
    for all GitHub operations needed by the agents.

    Attributes:
        client: PyGithub instance
        repo: GitHub repository object
        repo_name: Full repository name (owner/repo)
    """

    def __init__(self, token: str, repo_name: str):
        """
        Initialize GitHub client.

        Args:
            token: GitHub Personal Access Token
            repo_name: Full repository name (owner/repo)

        Example:
            >>> client = GitHubClient(
            ...     token="ghp_xxx",
            ...     repo_name="owner/repo"
            ... )
        """
        self.client = Github(token)
        self.repo_name = repo_name
        self.repo: Repository = self.client.get_repo(repo_name)

        logger.info(
            "GitHub client initialized",
            repo_name=repo_name
        )

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

        Raises:
            GithubException: If issue not found or API error
        """
        try:
            issue = self.repo.get_issue(issue_number)

            log_api_call(
                service="github",
                endpoint=f"/repos/{self.repo_name}/issues/{issue_number}",
                method="GET",
                status_code=200
            )

            return GitHubIssueWrapper(issue)

        except GithubException as e:
            logger.error(
                "Failed to get issue",
                issue_number=issue_number,
                error=str(e),
                status_code=e.status,
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If comment creation fails
        """
        with RequestLogger("create_issue_comment", issue_number=issue_number):
            try:
                issue = self.repo.get_issue(issue_number)
                issue.create_comment(comment_body)

                log_api_call(
                    service="github",
                    endpoint=f"/repos/{self.repo_name}/issues/{issue_number}/comments",
                    method="POST",
                    status_code=201
                )

                logger.info(
                    "Issue comment created",
                    issue_number=issue_number
                )

            except GithubException as e:
                logger.error(
                    "Failed to create issue comment",
                    issue_number=issue_number,
                    error=str(e),
                    status_code=e.status,
                    exc_info=True
                )
                raise

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

        Raises:
            GithubException: If adding labels fails
        """
        try:
            issue = self.repo.get_issue(issue_number)
            issue.add_to_labels(*labels)

            log_api_call(
                service="github",
                endpoint=f"/repos/{self.repo_name}/issues/{issue_number}/labels",
                method="POST",
                status_code=200
            )

            logger.info(
                "Labels added to issue",
                issue_number=issue_number,
                labels=labels
            )

        except GithubException as e:
            logger.error(
                "Failed to add labels",
                issue_number=issue_number,
                labels=labels,
                error=str(e),
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If removing labels fails
        """
        try:
            issue = self.repo.get_issue(issue_number)

            for label in labels:
                try:
                    issue.remove_from_labels(label)
                except GithubException:
                    # Label might not exist, continue
                    logger.warning(
                        "Label not found on issue",
                        issue_number=issue_number,
                        label=label
                    )

            logger.info(
                "Labels removed from issue",
                issue_number=issue_number,
                labels=labels
            )

        except GithubException as e:
            logger.error(
                "Failed to remove labels",
                issue_number=issue_number,
                error=str(e),
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If PR creation fails
        """
        with RequestLogger("create_pull_request", head_branch=head_branch):
            try:
                pr = self.repo.create_pull(
                    title=title,
                    body=body,
                    head=head_branch,
                    base=base_branch
                )

                log_api_call(
                    service="github",
                    endpoint=f"/repos/{self.repo_name}/pulls",
                    method="POST",
                    status_code=201
                )

                logger.info(
                    "Pull request created",
                    pr_number=pr.number,
                    head_branch=head_branch,
                    base_branch=base_branch
                )

                return GitHubPullRequestWrapper(pr)

            except GithubException as e:
                logger.error(
                    "Failed to create pull request",
                    head_branch=head_branch,
                    error=str(e),
                    status_code=e.status,
                    exc_info=True
                )
                raise

    def get_pull_request(self, pr_number: int) -> PullRequestProtocol:
        """
        Get pull request by number.

        Args:
            pr_number: PR number

        Returns:
            PullRequestProtocol: PR object

        Raises:
            GithubException: If PR not found
        """
        try:
            pr = self.repo.get_pull(pr_number)

            log_api_call(
                service="github",
                endpoint=f"/repos/{self.repo_name}/pulls/{pr_number}",
                method="GET",
                status_code=200
            )

            return GitHubPullRequestWrapper(pr)

        except GithubException as e:
            logger.error(
                "Failed to get pull request",
                pr_number=pr_number,
                error=str(e),
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If comment creation fails
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment_body)

            log_api_call(
                service="github",
                endpoint=f"/repos/{self.repo_name}/issues/{pr_number}/comments",
                method="POST",
                status_code=201
            )

            logger.info(
                "PR comment created",
                pr_number=pr_number
            )

        except GithubException as e:
            logger.error(
                "Failed to create PR comment",
                pr_number=pr_number,
                error=str(e),
                exc_info=True
            )
            raise

    def link_issue_to_pr(
        self,
        pr_number: int,
        issue_number: int
    ) -> None:
        """
        Link an issue to a pull request.

        This is done by adding "Closes #<issue_number>" to the PR body.

        Args:
            pr_number: PR number
            issue_number: Issue number to link

        Raises:
            GithubException: If linking fails
        """
        try:
            pr = self.repo.get_pull(pr_number)
            current_body = pr.body or ""

            # Add "Closes #X" if not already present
            closes_text = f"Closes #{issue_number}"
            if closes_text not in current_body:
                new_body = f"{current_body}\n\n{closes_text}"
                pr.edit(body=new_body)

                logger.info(
                    "Issue linked to PR",
                    pr_number=pr_number,
                    issue_number=issue_number
                )

        except GithubException as e:
            logger.error(
                "Failed to link issue to PR",
                pr_number=pr_number,
                issue_number=issue_number,
                error=str(e),
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If branch creation fails
        """
        try:
            # Get the SHA of the base branch
            base_ref = self.repo.get_git_ref(f"heads/{from_branch}")
            base_sha = base_ref.object.sha

            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )

            logger.info(
                "Branch created",
                branch_name=branch_name,
                from_branch=from_branch
            )

        except GithubException as e:
            logger.error(
                "Failed to create branch",
                branch_name=branch_name,
                error=str(e),
                exc_info=True
            )
            raise

    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if a branch exists.

        Args:
            branch_name: Branch name to check

        Returns:
            bool: True if branch exists
        """
        try:
            self.repo.get_git_ref(f"heads/{branch_name}")
            return True
        except GithubException:
            return False

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

        Raises:
            GithubException: If operation fails
        """
        try:
            # Try to get existing file
            try:
                existing_file = self.repo.get_contents(file_path, ref=branch)
                # Update existing file
                self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                logger.info("File updated", file_path=file_path, branch=branch)

            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    self.repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch=branch
                    )
                    logger.info("File created", file_path=file_path, branch=branch)
                else:
                    raise

        except GithubException as e:
            logger.error(
                "Failed to create/update file",
                file_path=file_path,
                error=str(e),
                exc_info=True
            )
            raise

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
        try:
            content_file = self.repo.get_contents(file_path, ref=branch)
            if isinstance(content_file, list):
                # It's a directory
                return None
            return content_file.decoded_content.decode("utf-8")

        except GithubException as e:
            if e.status == 404:
                return None
            logger.error(
                "Failed to get file content",
                file_path=file_path,
                error=str(e),
                exc_info=True
            )
            raise

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

        Raises:
            GithubException: If deletion fails
        """
        try:
            file = self.repo.get_contents(file_path, ref=branch)
            self.repo.delete_file(
                path=file_path,
                message=commit_message,
                sha=file.sha,
                branch=branch
            )

            logger.info("File deleted", file_path=file_path, branch=branch)

        except GithubException as e:
            logger.error(
                "Failed to delete file",
                file_path=file_path,
                error=str(e),
                exc_info=True
            )
            raise

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
        try:
            contents = self.repo.get_contents(path, ref=branch)

            if not isinstance(contents, list):
                contents = [contents]

            structure = []
            for item in contents:
                structure.append({
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "sha": item.sha
                })

            return structure

        except GithubException as e:
            logger.error(
                "Failed to get repository structure",
                path=path,
                error=str(e),
                exc_info=True
            )
            raise


def create_github_client(token: str, repo_name: str) -> GitHubClient:
    """
    Factory function to create a GitHub client.

    Args:
        token: GitHub Personal Access Token
        repo_name: Full repository name (owner/repo)

    Returns:
        GitHubClient: Configured client instance

    Example:
        >>> client = create_github_client(
        ...     token=settings.github_token,
        ...     repo_name=settings.github_repo
        ... )
    """
    return GitHubClient(token, repo_name)


def create_github_client_from_settings(settings) -> GitHubClient:
    """
    Create GitHub client from settings object.

    Args:
        settings: Settings instance

    Returns:
        GitHubClient: Configured client instance

    Example:
        >>> from src.config.settings import get_settings
        >>> settings = get_settings()
        >>> client = create_github_client_from_settings(settings)
    """
    return create_github_client(
        token=settings.github_token,
        repo_name=settings.github_repo
    )
