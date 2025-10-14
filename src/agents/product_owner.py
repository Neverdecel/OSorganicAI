"""
Product Owner Agent for OSOrganicAI.

This agent handles requirement refinement and issue clarification.
It inherits from BaseAgent and provides GENERIC scaffolding that
child instances will specialize for their domain.

Child instances customize via:
- get_domain_context(): Add domain-specific context (e-commerce, fintech, etc.)
- get_system_prompt(): Can override to adjust PO behavior

This is the TEMPLATE version - generic and reusable.
"""

from typing import Optional, List, Dict, Any
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import BaseMessage, HumanMessage

from src.agents.base import BaseAgent
from src.models.issue_analysis import IssueAnalysis, ConversationState
from src.utils.logger import log_function_call


class ProductOwnerAgent(BaseAgent):
    """
    Generic Product Owner Agent scaffold.

    This agent analyzes GitHub issues, asks clarifying questions,
    and refines requirements before marking them ready for development.

    **Template Pattern:**
    - Core workflow defined here (generic)
    - Domain context added by child instances
    - System prompt customizable by children

    **Extension Points for Children:**
    - get_domain_context(): Add domain-specific knowledge
    - get_system_prompt(): Customize PO personality/focus
    - customize_prompt(): Add extra prompt engineering
    """

    def get_system_prompt(self) -> str:
        """
        Get generic Product Owner system prompt.

        Child instances can override to customize behavior,
        but this default provides solid PO capabilities.

        Returns:
            str: System prompt defining PO role
        """
        return """You are an expert Product Owner and Business Analyst.

Your role is to:
1. **Analyze** feature requests and issue descriptions
2. **Identify** missing information or ambiguities
3. **Ask** clarifying questions to understand requirements fully
4. **Refine** requirements into clear, actionable specifications
5. **Estimate** complexity and effort
6. **Define** acceptance criteria

## Guidelines:
- Ask specific, focused questions (not generic ones)
- Think about edge cases and error handling
- Consider non-functional requirements (performance, security, UX)
- Be concise but thorough
- Use your expertise to anticipate what developers will need

## Output Format:
Always respond with structured JSON matching the IssueAnalysis schema.
Be precise and actionable in your analysis."""

    def get_domain_context(self) -> str:
        """
        Get domain context (empty in template, specialized by children).

        **Child instances MUST override this** to add domain knowledge.

        Returns:
            str: Empty string (no domain context in template)

        Example (in child instance):
            >>> def get_domain_context(self) -> str:
            ...     return '''
            ...     E-commerce platform context:
            ...     - Always consider inventory availability
            ...     - Ensure PCI-DSS compliance for payments
            ...     - Think about shipping logistics
            ...     '''
        """
        return ""

    @log_function_call
    def analyze_issue(
        self,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        existing_labels: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> IssueAnalysis:
        """
        Analyze a GitHub issue and determine if clarification is needed.

        This is the main entry point for the Product Owner Agent.
        Uses LangChain with structured output (Pydantic parser).

        Args:
            issue_number: GitHub issue number
            issue_title: Issue title
            issue_body: Issue description
            existing_labels: Current issue labels
            additional_context: Optional additional context

        Returns:
            IssueAnalysis: Structured analysis result

        Example:
            >>> analysis = agent.analyze_issue(
            ...     issue_number=42,
            ...     issue_title="Add shopping cart",
            ...     issue_body="Users should be able to add items to cart"
            ... )
            >>> if analysis.needs_clarification:
            ...     print(analysis.questions)
        """
        self.logger.info(
            "Analyzing issue",
            issue_number=issue_number,
            issue_title=issue_title
        )

        # Set up Pydantic parser for structured output
        parser = PydanticOutputParser(pydantic_object=IssueAnalysis)

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(
            issue_title=issue_title,
            issue_body=issue_body,
            existing_labels=existing_labels,
            format_instructions=parser.get_format_instructions()
        )

        # Build LangChain messages
        messages = self.build_messages(
            user_input=prompt,
            additional_context=additional_context
        )

        # Invoke LLM with retry
        response = self.invoke_with_retry(messages)

        # Parse structured output
        try:
            analysis = parser.parse(response)
        except Exception as e:
            self.logger.error(
                "Failed to parse LLM response",
                error=str(e),
                response_preview=response[:500],
                exc_info=True
            )
            raise

        # Log the analysis
        self.log_action(
            action_type="issue_analyzed",
            payload={
                "issue_number": issue_number,
                "needs_clarification": analysis.needs_clarification,
                "question_count": len(analysis.questions),
                "estimated_complexity": analysis.estimated_complexity,
            }
        )

        self.logger.info(
            "Issue analysis complete",
            issue_number=issue_number,
            needs_clarification=analysis.needs_clarification,
            is_complete=analysis.is_complete
        )

        return analysis

    def _build_analysis_prompt(
        self,
        issue_title: str,
        issue_body: str,
        existing_labels: Optional[List[str]],
        format_instructions: str
    ) -> str:
        """
        Build the analysis prompt for the LLM.

        Args:
            issue_title: Issue title
            issue_body: Issue description
            existing_labels: Current labels
            format_instructions: Pydantic parser format instructions

        Returns:
            str: Formatted prompt
        """
        prompt = f"""Analyze this GitHub issue and provide a structured assessment.

## Issue Information
**Title:** {issue_title}

**Description:**
{issue_body}

**Existing Labels:** {', '.join(existing_labels) if existing_labels else 'None'}

## Your Task
Analyze this issue thoroughly and determine:
1. Is the requirement clear enough for development?
2. What clarifying questions should be asked?
3. What is the estimated complexity?
4. What acceptance criteria should be defined?
5. Are there technical considerations to note?

## Output Format
{format_instructions}

**Important:**
- If you need ANY clarification, set needs_clarification=true and provide specific questions
- If everything is crystal clear, set is_complete=true and provide refined_description
- Be specific and actionable in your questions and analysis
"""
        return prompt

    @log_function_call
    def ask_clarifying_questions(
        self,
        issue_number: int,
        questions: List[str]
    ) -> None:
        """
        Post clarifying questions as a GitHub comment.

        Args:
            issue_number: GitHub issue number
            questions: List of questions to ask

        Example:
            >>> agent.ask_clarifying_questions(
            ...     issue_number=42,
            ...     questions=["What payment methods?", "Guest checkout?"]
            ... )
        """
        self.logger.info(
            "Asking clarifying questions",
            issue_number=issue_number,
            question_count=len(questions)
        )

        # Format questions as Markdown
        comment_body = "## 🤔 Clarification Needed\n\n"
        comment_body += "To better understand this requirement, I have some questions:\n\n"

        for i, question in enumerate(questions, 1):
            comment_body += f"{i}. {question}\n"

        comment_body += "\nPlease provide answers so I can refine the requirements for development."

        # Format with agent signature
        formatted_comment = self.format_github_comment(comment_body)

        # Post to GitHub
        self.vcs_client.create_issue_comment(issue_number, formatted_comment)

        # Add label
        self.vcs_client.add_labels_to_issue(issue_number, ["needs-clarification"])

        # Log action
        self.log_action(
            action_type="questions_asked",
            payload={
                "issue_number": issue_number,
                "questions": questions
            }
        )

    @log_function_call
    def mark_ready_for_development(
        self,
        issue_number: int,
        refined_description: str,
        acceptance_criteria: List[str],
        suggested_labels: List[str]
    ) -> None:
        """
        Mark issue as ready for development with refined requirements.

        Args:
            issue_number: GitHub issue number
            refined_description: Refined requirement description
            acceptance_criteria: List of acceptance criteria
            suggested_labels: Labels to add

        Example:
            >>> agent.mark_ready_for_development(
            ...     issue_number=42,
            ...     refined_description="Implement cart with session persistence",
            ...     acceptance_criteria=["Users can add items", "Cart persists"],
            ...     suggested_labels=["feature", "ready-for-dev"]
            ... )
        """
        self.logger.info(
            "Marking issue ready for development",
            issue_number=issue_number
        )

        # Format refined requirements as comment
        comment_body = "## ✅ Requirements Refined\n\n"
        comment_body += f"**Refined Description:**\n{refined_description}\n\n"

        if acceptance_criteria:
            comment_body += "**Acceptance Criteria:**\n"
            for i, criterion in enumerate(acceptance_criteria, 1):
                comment_body += f"{i}. {criterion}\n"
            comment_body += "\n"

        comment_body += "This issue is now ready for development!"

        # Format with signature
        formatted_comment = self.format_github_comment(comment_body)

        # Post to GitHub
        self.vcs_client.create_issue_comment(issue_number, formatted_comment)

        # Update labels
        self.vcs_client.remove_labels_from_issue(issue_number, ["needs-clarification"])
        self.vcs_client.add_labels_to_issue(issue_number, suggested_labels + ["ready-for-dev"])

        # Log action
        self.log_action(
            action_type="marked_ready_for_dev",
            payload={
                "issue_number": issue_number,
                "refined_description": refined_description,
                "acceptance_criteria_count": len(acceptance_criteria)
            }
        )

    @log_function_call
    def process_user_response(
        self,
        conversation_id: str,
        user_responses: List[str]
    ) -> IssueAnalysis:
        """
        Process user's answers to clarifying questions.

        Re-analyzes the issue with the new information to determine
        if more clarification is needed or if it's ready for dev.

        Args:
            conversation_id: Conversation UUID
            user_responses: User's answers to previous questions

        Returns:
            IssueAnalysis: Updated analysis

        Example:
            >>> analysis = agent.process_user_response(
            ...     conversation_id="uuid",
            ...     user_responses=["Stripe and PayPal", "Yes, support guest checkout"]
            ... )
        """
        self.logger.info(
            "Processing user response",
            conversation_id=conversation_id,
            response_count=len(user_responses)
        )

        # Get conversation from database
        # (In a full implementation, we'd fetch the full conversation history)
        # For now, we'll create a simplified follow-up analysis

        # Build follow-up prompt
        prompt = f"""Based on the user's responses to clarifying questions, re-analyze the requirement.

## User Responses:
{chr(10).join(f"{i}. {response}" for i, response in enumerate(user_responses, 1))}

## Your Task:
Determine if:
1. All questions have been adequately answered
2. The requirement is now clear enough for development
3. More clarification is still needed

Provide an updated IssueAnalysis."""

        # Set up parser
        parser = PydanticOutputParser(pydantic_object=IssueAnalysis)
        prompt += f"\n\n{parser.get_format_instructions()}"

        # Build messages
        messages = self.build_messages(user_input=prompt)

        # Invoke LLM
        response = self.invoke_with_retry(messages)

        # Parse response
        analysis = parser.parse(response)

        # Log action
        self.log_action(
            action_type="user_response_processed",
            payload={
                "conversation_id": conversation_id,
                "still_needs_clarification": analysis.needs_clarification,
                "is_complete": analysis.is_complete
            },
            conversation_id=conversation_id
        )

        return analysis

    @log_function_call
    def handle_issue_workflow(
        self,
        issue_number: int,
        issue_id: int,
        issue_title: str,
        issue_body: str,
        repo_full_name: str
    ) -> ConversationState:
        """
        Complete workflow for handling a new issue.

        This orchestrates the entire process:
        1. Create conversation record
        2. Analyze the issue
        3. Post questions OR mark ready for dev

        Args:
            issue_number: GitHub issue number
            issue_id: GitHub issue ID
            issue_title: Issue title
            issue_body: Issue description
            repo_full_name: Full repo name (owner/repo)

        Returns:
            ConversationState: Current conversation state

        Example:
            >>> state = agent.handle_issue_workflow(
            ...     issue_number=42,
            ...     issue_id=123456,
            ...     issue_title="Add cart",
            ...     issue_body="Users need shopping cart",
            ...     repo_full_name="org/repo"
            ... )
        """
        self.logger.info(
            "Starting issue workflow",
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        # Get or create conversation
        conversation_id = self.get_or_create_conversation(
            issue_number=issue_number,
            issue_id=issue_id,
            repo_full_name=repo_full_name
        )

        # Analyze issue
        analysis = self.analyze_issue(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body
        )

        # Update conversation with analysis
        self.update_conversation_state(
            conversation_id=conversation_id,
            status="needs_clarification" if analysis.needs_clarification else "ready_for_dev",
            analysis=analysis.model_dump()
        )

        # Take action based on analysis
        if analysis.needs_clarification:
            # Ask questions
            self.ask_clarifying_questions(
                issue_number=issue_number,
                questions=analysis.questions
            )
        elif analysis.is_complete:
            # Mark ready for dev
            self.mark_ready_for_development(
                issue_number=issue_number,
                refined_description=analysis.refined_description or issue_body,
                acceptance_criteria=analysis.acceptance_criteria,
                suggested_labels=analysis.suggested_labels
            )

        # Build conversation state (simplified)
        state = ConversationState(
            issue_id=issue_id,
            issue_number=issue_number,
            repo_full_name=repo_full_name,
            status="needs_clarification" if analysis.needs_clarification else "ready_for_dev",
            current_analysis=analysis
        )

        self.logger.info(
            "Issue workflow complete",
            issue_number=issue_number,
            status=state.status
        )

        return state
