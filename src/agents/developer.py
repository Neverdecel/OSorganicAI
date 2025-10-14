"""
Developer Agent for OSOrganicAI.

This agent handles code generation, testing, and pull request creation.
It inherits from BaseAgent and provides GENERIC scaffolding that
child instances will specialize for their tech stack.

Child instances customize via:
- get_domain_context(): Add tech stack specific context (languages, frameworks)
- get_system_prompt(): Can override to adjust developer behavior
- get_tech_stack_context(): Define programming languages and frameworks

This is the TEMPLATE version - generic and reusable.
"""

from typing import Optional, List, Dict, Any
from langchain.output_parsers import PydanticOutputParser

from src.agents.base import BaseAgent
from src.models.code_generation import (
    CodeGeneration,
    CodeGenerationResult,
    FileChange
)
from src.utils.logger import log_function_call


class DeveloperAgent(BaseAgent):
    """
    Generic Developer Agent scaffold.

    This agent generates code, writes tests, and creates pull requests
    based on refined requirements.

    **Template Pattern:**
    - Core workflow defined here (generic)
    - Tech stack context added by child instances
    - System prompt customizable by children

    **Extension Points for Children:**
    - get_domain_context(): Add tech stack and patterns
    - get_tech_stack_context(): Define languages/frameworks
    - get_system_prompt(): Customize developer personality
    """

    def get_system_prompt(self) -> str:
        """
        Get generic Developer system prompt.

        Child instances can override to customize behavior.

        Returns:
            str: System prompt defining developer role
        """
        return """You are a senior software engineer with expertise in writing clean, maintainable code.

Your role is to:
1. **Understand** requirements and technical specifications
2. **Design** elegant solutions following best practices
3. **Implement** code with proper error handling
4. **Write** comprehensive tests (unit, integration)
5. **Document** code with clear comments and docstrings
6. **Follow** SOLID principles and design patterns

## Code Quality Standards:
- Write clean, readable, self-documenting code
- Include error handling and edge cases
- Add type hints/annotations where applicable
- Write docstrings for functions and classes
- Follow language-specific conventions
- Keep functions small and focused (SRP)
- Avoid code duplication (DRY)

## Testing Standards:
- Write tests that cover happy path and edge cases
- Use meaningful test names that describe behavior
- Aim for high code coverage (80%+)
- Test both success and failure scenarios
- Mock external dependencies appropriately

## Output Format:
Always respond with structured JSON matching the CodeGeneration schema.
Be precise and include all necessary files."""

    def get_domain_context(self) -> str:
        """
        Get domain context (empty in template, specialized by children).

        **Child instances SHOULD override this** to add tech stack info.

        Returns:
            str: Empty string (no domain context in template)

        Example (in child instance):
            >>> def get_domain_context(self) -> str:
            ...     return '''
            ...     Tech Stack:
            ...     - Language: Python 3.10+
            ...     - Framework: FastAPI
            ...     - Database: PostgreSQL via Supabase
            ...     - Testing: pytest
            ...     - Style: Black, flake8, mypy
            ...     '''
        """
        return ""

    def get_tech_stack_context(self) -> Dict[str, Any]:
        """
        Get tech stack information.

        Child instances override this to specify their stack.

        Returns:
            Dict[str, Any]: Tech stack configuration

        Example (in child instance):
            >>> def get_tech_stack_context(self) -> Dict[str, Any]:
            ...     return {
            ...         "language": "python",
            ...         "version": "3.10+",
            ...         "frameworks": ["fastapi", "langchain"],
            ...         "testing": "pytest",
            ...         "linting": ["black", "flake8", "mypy"]
            ...     }
        """
        return {
            "language": "python",
            "version": "3.10+",
            "testing": "pytest"
        }

    @log_function_call
    def generate_code(
        self,
        issue_number: int,
        requirements: str,
        acceptance_criteria: List[str],
        codebase_context: Optional[str] = None
    ) -> CodeGeneration:
        """
        Generate code based on requirements.

        This is the main entry point for the Developer Agent.
        Uses LangChain with structured output (Pydantic parser).

        Args:
            issue_number: GitHub issue number
            requirements: Refined requirement description
            acceptance_criteria: List of acceptance criteria
            codebase_context: Optional context about existing codebase

        Returns:
            CodeGeneration: Structured code generation result

        Example:
            >>> code_gen = agent.generate_code(
            ...     issue_number=42,
            ...     requirements="Implement shopping cart with session persistence",
            ...     acceptance_criteria=["Users can add items", "Cart persists"]
            ... )
        """
        self.logger.info(
            "Generating code",
            issue_number=issue_number
        )

        # Get tech stack context
        tech_stack = self.get_tech_stack_context()

        # Set up Pydantic parser
        parser = PydanticOutputParser(pydantic_object=CodeGeneration)

        # Build the generation prompt
        prompt = self._build_generation_prompt(
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            tech_stack=tech_stack,
            codebase_context=codebase_context,
            format_instructions=parser.get_format_instructions()
        )

        # Build LangChain messages
        messages = self.build_messages(user_input=prompt)

        # Invoke LLM with retry
        response = self.invoke_with_retry(messages)

        # Parse structured output
        try:
            code_gen = parser.parse(response)
        except Exception as e:
            self.logger.error(
                "Failed to parse LLM response",
                error=str(e),
                response_preview=response[:500],
                exc_info=True
            )
            raise

        # Log the generation
        self.log_action(
            action_type="code_generated",
            payload={
                "issue_number": issue_number,
                "files_count": len(code_gen.files_to_create),
                "tests_count": len(code_gen.test_files),
                "branch_name": code_gen.branch_name
            }
        )

        self.logger.info(
            "Code generation complete",
            issue_number=issue_number,
            files_count=len(code_gen.files_to_create),
            tests_count=len(code_gen.test_files)
        )

        return code_gen

    def _build_generation_prompt(
        self,
        requirements: str,
        acceptance_criteria: List[str],
        tech_stack: Dict[str, Any],
        codebase_context: Optional[str],
        format_instructions: str
    ) -> str:
        """
        Build the code generation prompt for the LLM.

        Args:
            requirements: Requirement description
            acceptance_criteria: Acceptance criteria
            tech_stack: Tech stack information
            codebase_context: Existing codebase context
            format_instructions: Pydantic parser format instructions

        Returns:
            str: Formatted prompt
        """
        # Format tech stack
        tech_stack_str = "\n".join(
            f"- {key}: {value}"
            for key, value in tech_stack.items()
        )

        # Format acceptance criteria
        criteria_str = "\n".join(
            f"{i}. {criterion}"
            for i, criterion in enumerate(acceptance_criteria, 1)
        )

        prompt = f"""Generate production-ready code to implement this requirement.

## Requirements
{requirements}

## Acceptance Criteria
{criteria_str}

## Tech Stack
{tech_stack_str}
"""

        if codebase_context:
            prompt += f"""
## Existing Codebase Context
{codebase_context}
"""

        prompt += f"""
## Your Task
Generate:
1. **Implementation files** with clean, well-documented code
2. **Test files** with comprehensive test coverage
3. **Commit message** following conventional commits format
4. **PR description** with summary and test plan
5. **Branch name** (e.g., feature/shopping-cart)

## Requirements:
- Follow SOLID principles
- Include error handling
- Add type hints/annotations
- Write clear docstrings
- Create comprehensive tests
- Consider edge cases

## Output Format
{format_instructions}

**Important:**
- Provide COMPLETE file contents, not snippets
- Include all necessary imports
- Ensure code is production-ready
- Tests should be runnable
"""
        return prompt

    @log_function_call
    def create_pull_request(
        self,
        conversation_id: str,
        issue_number: int,
        code_generation: CodeGeneration
    ) -> CodeGenerationResult:
        """
        Create branch, commit files, and open pull request.

        This orchestrates the entire PR creation process.

        Args:
            conversation_id: Conversation UUID
            issue_number: GitHub issue number
            code_generation: Generated code and metadata

        Returns:
            CodeGenerationResult: Result with PR information

        Example:
            >>> result = agent.create_pull_request(
            ...     conversation_id="uuid",
            ...     issue_number=42,
            ...     code_generation=code_gen
            ... )
            >>> print(f"PR created: {result.pr_url}")
        """
        self.logger.info(
            "Creating pull request",
            issue_number=issue_number,
            branch_name=code_generation.branch_name
        )

        try:
            # Create branch if it doesn't exist
            if not self.vcs_client.branch_exists(code_generation.branch_name):
                self.vcs_client.create_branch(code_generation.branch_name)
                self.logger.info("Branch created", branch=code_generation.branch_name)

            # Commit all files
            for file_change in code_generation.files_to_create:
                self.vcs_client.create_or_update_file(
                    file_path=file_change.file_path,
                    content=file_change.content,
                    commit_message=f"Add {file_change.file_path}",
                    branch=code_generation.branch_name
                )
                self.logger.info("File committed", file_path=file_change.file_path)

            # Commit all test files
            for test_file in code_generation.test_files:
                self.vcs_client.create_or_update_file(
                    file_path=test_file.file_path,
                    content=test_file.content,
                    commit_message=f"Add tests: {test_file.file_path}",
                    branch=code_generation.branch_name
                )
                self.logger.info("Test file committed", file_path=test_file.file_path)

            # Create pull request
            pr = self.vcs_client.create_pull_request(
                title=code_generation.pr_title,
                body=code_generation.pr_description,
                head_branch=code_generation.branch_name,
                base_branch="main"
            )

            # Link issue to PR
            self.vcs_client.link_issue_to_pr(
                pr_number=pr.number,
                issue_number=issue_number
            )

            # Create code generation record in database
            generation_id = self.db_client.create_code_generation(
                conversation_id=conversation_id,
                pr_number=pr.number,
                files_changed={"files": [f.model_dump() for f in code_generation.files_to_create]},
                tests_generated={"tests": [t.model_dump() for t in code_generation.test_files]},
                status="pr_created"
            )

            # Log action
            self.log_action(
                action_type="pr_created",
                payload={
                    "pr_number": pr.number,
                    "issue_number": issue_number,
                    "branch_name": code_generation.branch_name,
                    "files_count": len(code_generation.files_to_create),
                    "tests_count": len(code_generation.test_files)
                },
                conversation_id=conversation_id
            )

            # Build result
            result = CodeGenerationResult(
                generation=code_generation,
                pr_number=pr.number,
                pr_url=f"https://github.com/{self.vcs_client.repo_name}/pull/{pr.number}",
                status="pr_created"
            )

            self.logger.info(
                "Pull request created successfully",
                pr_number=pr.number,
                issue_number=issue_number
            )

            return result

        except Exception as e:
            self.logger.error(
                "Failed to create pull request",
                issue_number=issue_number,
                error=str(e),
                exc_info=True
            )

            # Create failed generation record
            generation_id = self.db_client.create_code_generation(
                conversation_id=conversation_id,
                pr_number=None,
                files_changed={"files": [f.model_dump() for f in code_generation.files_to_create]},
                tests_generated={"tests": [t.model_dump() for t in code_generation.test_files]},
                status="failed"
            )

            # Update with error
            self.db_client.update_code_generation_status(
                generation_id=generation_id,
                status="failed",
                error_message=str(e)
            )

            # Return result with error
            result = CodeGenerationResult(
                generation=code_generation,
                status="failed",
                error_message=str(e)
            )

            return result

    @log_function_call
    def handle_ready_for_dev_issue(
        self,
        conversation_id: str,
        issue_number: int,
        requirements: str,
        acceptance_criteria: List[str]
    ) -> CodeGenerationResult:
        """
        Complete workflow for handling a ready-for-dev issue.

        This orchestrates the entire process:
        1. Generate code
        2. Create branch and commit
        3. Open pull request

        Args:
            conversation_id: Conversation UUID
            issue_number: GitHub issue number
            requirements: Refined requirements
            acceptance_criteria: Acceptance criteria

        Returns:
            CodeGenerationResult: Result with PR information

        Example:
            >>> result = agent.handle_ready_for_dev_issue(
            ...     conversation_id="uuid",
            ...     issue_number=42,
            ...     requirements="Implement cart with persistence",
            ...     acceptance_criteria=["Users can add items"]
            ... )
        """
        self.logger.info(
            "Starting development workflow",
            issue_number=issue_number
        )

        # Generate code
        code_generation = self.generate_code(
            issue_number=issue_number,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria
        )

        # Create PR
        result = self.create_pull_request(
            conversation_id=conversation_id,
            issue_number=issue_number,
            code_generation=code_generation
        )

        # Post comment on issue
        if result.pr_url:
            comment = self.format_github_comment(
                f"## 🚀 Pull Request Created\n\n"
                f"I've implemented this feature and created a pull request:\n\n"
                f"**PR:** {result.pr_url}\n"
                f"**Branch:** `{code_generation.branch_name}`\n\n"
                f"**Changes:**\n"
                f"- {len(code_generation.files_to_create)} implementation files\n"
                f"- {len(code_generation.test_files)} test files\n\n"
                f"The CI/CD pipeline will run automated tests. "
                f"Once tests pass, the PR will be ready for review."
            )
            self.vcs_client.create_issue_comment(issue_number, comment)

        self.logger.info(
            "Development workflow complete",
            issue_number=issue_number,
            pr_number=result.pr_number
        )

        return result
