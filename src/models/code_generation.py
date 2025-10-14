"""
Pydantic models for Developer Agent code generation.

These models define the structured output format for code generation,
ensuring type safety and validation throughout the system.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class FileChange(BaseModel):
    """
    Represents a single file to be created or modified.

    Contains the file path, content, and metadata.
    """

    file_path: str = Field(
        description="Relative path to the file from project root"
    )

    content: str = Field(
        description="Full content of the file"
    )

    operation: str = Field(
        default="create",
        description="Operation type: 'create', 'modify', or 'delete'"
    )

    language: Optional[str] = Field(
        default=None,
        description="Programming language of the file"
    )

    description: str = Field(
        description="Brief description of what this file does"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "file_path": "src/services/payment.py",
                "content": "def process_payment(...):\n    pass",
                "operation": "create",
                "language": "python",
                "description": "Payment processing service"
            }
        }


class TestFile(BaseModel):
    """
    Represents a test file with test cases.

    Contains test file path, content, and metadata about test coverage.
    """

    file_path: str = Field(
        description="Relative path to the test file"
    )

    content: str = Field(
        description="Full content of the test file"
    )

    test_framework: str = Field(
        description="Test framework used (e.g., 'pytest', 'jest', 'junit')"
    )

    test_count: int = Field(
        ge=0,
        description="Number of test cases in this file"
    )

    coverage_targets: List[str] = Field(
        default_factory=list,
        description="List of functions/classes being tested"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "file_path": "tests/test_payment.py",
                "content": "def test_process_payment():\n    pass",
                "test_framework": "pytest",
                "test_count": 5,
                "coverage_targets": ["process_payment", "validate_card"]
            }
        }


class CodeGeneration(BaseModel):
    """
    Structured output for Developer Agent's code generation.

    Contains all files to be created/modified, tests, and PR metadata.
    """

    files_to_create: List[FileChange] = Field(
        default_factory=list,
        description="List of implementation files to create or modify"
    )

    test_files: List[TestFile] = Field(
        default_factory=list,
        description="List of test files to create"
    )

    commit_message: str = Field(
        description="Git commit message following conventional commits format"
    )

    pr_title: str = Field(
        description="Pull request title"
    )

    pr_description: str = Field(
        description="Detailed pull request description in Markdown"
    )

    branch_name: str = Field(
        description="Git branch name for this change"
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="New dependencies to add (e.g., pip packages, npm packages)"
    )

    environment_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="New environment variables needed"
    )

    migration_steps: List[str] = Field(
        default_factory=list,
        description="Manual migration steps required (e.g., database migrations)"
    )

    breaking_changes: List[str] = Field(
        default_factory=list,
        description="List of breaking changes (if any)"
    )

    estimated_test_time_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated time for tests to run"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "files_to_create": [],
                "test_files": [],
                "commit_message": "feat: add payment processing service\n\nImplements Stripe payment integration",
                "pr_title": "Add payment processing service",
                "pr_description": "## Summary\n- Adds payment service\n- Includes tests",
                "branch_name": "feature/payment-processing",
                "dependencies": ["stripe==5.0.0"],
                "environment_variables": {"STRIPE_API_KEY": "your-key-here"},
                "migration_steps": [],
                "breaking_changes": [],
                "estimated_test_time_seconds": 30
            }
        }


class CodeReview(BaseModel):
    """
    Structured output for code review analysis.

    Used by review agents or for self-review before PR creation.
    """

    overall_quality: str = Field(
        description="Overall code quality: 'excellent', 'good', 'needs_improvement', 'poor'"
    )

    issues_found: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of issues found with severity and description"
    )

    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )

    security_concerns: List[str] = Field(
        default_factory=list,
        description="Security concerns identified"
    )

    performance_concerns: List[str] = Field(
        default_factory=list,
        description="Performance concerns identified"
    )

    test_coverage_percentage: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Estimated test coverage percentage"
    )

    follows_best_practices: bool = Field(
        default=True,
        description="Whether code follows established best practices"
    )

    approved: bool = Field(
        default=True,
        description="Whether the code is approved for merge"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "overall_quality": "good",
                "issues_found": [
                    {
                        "severity": "medium",
                        "description": "Missing error handling in payment function"
                    }
                ],
                "suggestions": ["Add input validation", "Improve error messages"],
                "security_concerns": [],
                "performance_concerns": [],
                "test_coverage_percentage": 85.0,
                "follows_best_practices": True,
                "approved": True
            }
        }


class CodeGenerationResult(BaseModel):
    """
    Complete result of code generation including review.

    Combines the generated code with self-review analysis.
    """

    generation: CodeGeneration = Field(
        description="Generated code and metadata"
    )

    review: Optional[CodeReview] = Field(
        default=None,
        description="Self-review of generated code"
    )

    pr_number: Optional[int] = Field(
        default=None,
        description="PR number once created"
    )

    pr_url: Optional[str] = Field(
        default=None,
        description="URL to the created pull request"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the code was generated"
    )

    status: str = Field(
        default="generated",
        description="Status: 'generated', 'pr_created', 'merged', 'failed'"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if generation or PR creation failed"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "generation": {},
                "review": None,
                "pr_number": 42,
                "pr_url": "https://github.com/org/repo/pull/42",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "pr_created",
                "error_message": None
            }
        }
