"""
Pydantic models for Product Owner Agent issue analysis.

These models define the structured output format for issue analysis,
ensuring type safety and validation throughout the system.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class IssueAnalysis(BaseModel):
    """
    Structured output for Product Owner Agent's issue analysis.

    This model represents the result of analyzing a GitHub issue
    to determine if clarification is needed and what questions to ask.
    """

    needs_clarification: bool = Field(
        description="Whether the issue requires clarification before development"
    )

    questions: List[str] = Field(
        default_factory=list,
        description="List of clarifying questions to ask the user"
    )

    refined_description: Optional[str] = Field(
        default=None,
        description="Refined and detailed requirement description"
    )

    is_complete: bool = Field(
        default=False,
        description="Whether the requirements are complete and ready for development"
    )

    estimated_complexity: str = Field(
        description="Estimated complexity: 'low', 'medium', or 'high'"
    )

    suggested_labels: List[str] = Field(
        default_factory=list,
        description="Suggested GitHub labels for the issue"
    )

    acceptance_criteria: List[str] = Field(
        default_factory=list,
        description="List of acceptance criteria for the feature"
    )

    technical_considerations: List[str] = Field(
        default_factory=list,
        description="Technical considerations and potential challenges"
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependencies on other issues or components"
    )

    estimated_effort_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Estimated effort in hours"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "needs_clarification": True,
                "questions": [
                    "What payment methods should be supported?",
                    "Should we support guest checkout?"
                ],
                "refined_description": None,
                "is_complete": False,
                "estimated_complexity": "medium",
                "suggested_labels": ["feature", "payment"],
                "acceptance_criteria": [],
                "technical_considerations": [],
                "dependencies": [],
                "estimated_effort_hours": None
            }
        }


class ConversationTurn(BaseModel):
    """
    Represents a single turn in the conversation with the user.

    Tracks both the agent's questions and the user's responses.
    """

    turn_number: int = Field(
        ge=1,
        description="Sequential turn number in the conversation"
    )

    agent_questions: List[str] = Field(
        description="Questions asked by the agent in this turn"
    )

    user_responses: Optional[List[str]] = Field(
        default=None,
        description="User's responses to the questions"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this turn occurred"
    )


class ConversationState(BaseModel):
    """
    Maintains the state of an ongoing conversation about an issue.

    Tracks all conversation turns and the current analysis state.
    """

    issue_id: int = Field(
        description="GitHub issue ID"
    )

    issue_number: int = Field(
        description="GitHub issue number"
    )

    repo_full_name: str = Field(
        description="Full repository name (owner/repo)"
    )

    status: str = Field(
        default="analyzing",
        description="Current status: 'analyzing', 'needs_clarification', 'ready_for_dev'"
    )

    turns: List[ConversationTurn] = Field(
        default_factory=list,
        description="All conversation turns"
    )

    current_analysis: Optional[IssueAnalysis] = Field(
        default=None,
        description="Current issue analysis state"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation started"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was last updated"
    )

    def add_turn(
        self,
        agent_questions: List[str],
        user_responses: Optional[List[str]] = None
    ) -> ConversationTurn:
        """
        Add a new conversation turn.

        Args:
            agent_questions: Questions asked by the agent
            user_responses: Optional user responses

        Returns:
            ConversationTurn: The newly created turn
        """
        turn = ConversationTurn(
            turn_number=len(self.turns) + 1,
            agent_questions=agent_questions,
            user_responses=user_responses
        )
        self.turns.append(turn)
        self.updated_at = datetime.utcnow()
        return turn

    def update_analysis(self, analysis: IssueAnalysis) -> None:
        """
        Update the current analysis and status.

        Args:
            analysis: New issue analysis
        """
        self.current_analysis = analysis
        self.updated_at = datetime.utcnow()

        # Update status based on analysis
        if analysis.is_complete:
            self.status = "ready_for_dev"
        elif analysis.needs_clarification:
            self.status = "needs_clarification"
        else:
            self.status = "analyzing"

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "issue_id": 123456789,
                "issue_number": 42,
                "repo_full_name": "org/repo",
                "status": "needs_clarification",
                "turns": [],
                "current_analysis": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:05:00Z"
            }
        }
