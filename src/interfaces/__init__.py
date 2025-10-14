"""
Protocol interfaces for OSOrganicAI.

This module exports all protocol interfaces used throughout the application.
Following the Interface Segregation Principle (ISP) and Dependency Inversion Principle (DIP).
"""

from src.interfaces.vcs_client import (
    VCSClientProtocol,
    IssueProtocol,
    PullRequestProtocol,
)

from src.interfaces.database_client import (
    DatabaseClientProtocol,
)


__all__ = [
    # VCS Protocols
    "VCSClientProtocol",
    "IssueProtocol",
    "PullRequestProtocol",
    # Database Protocols
    "DatabaseClientProtocol",
]
