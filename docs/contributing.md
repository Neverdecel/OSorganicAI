# 🤝 Contributing to OSOrganicAI

Thank you for your interest in contributing to OSOrganicAI! This document provides guidelines for contributing to the **mother repository** (meta-template).

---

## 🏭 Understanding the Meta-Template

OSOrganicAI is a **mother repository** — a living template that spawns child instances. When you contribute here, you're improving:

- **Generic agent scaffolds** that all children inherit
- **Template structures** used to spawn new instances
- **Core documentation** and conventions
- **Testing infrastructure** (the internal `test-child/`)

### Mother vs. Child Contributions

| Mother Repository (This Repo) | Child Instances (Spawned Projects) |
|-------------------------------|-------------------------------------|
| Generic, reusable patterns | Domain-specific implementations |
| Base agent classes | Specialized agents |
| Template documentation | Project-specific docs |
| Test-child validation | Production systems |
| **You're contributing here** | **Not covered by this guide** |

**This guide covers mother repository contributions only.** If you're working on a child instance, adapt these guidelines for your project.

---

## 📜 Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

---

## 🎯 How Can I Contribute?

### 1. **Reporting Bugs**

If you find a bug, please create an issue with:

- **Clear title** describing the problem
- **Detailed description** of what happened
- **Steps to reproduce** the issue
- **Expected behavior** vs. actual behavior
- **Environment details** (OS, Python version, etc.)
- **Screenshots or logs** if applicable

**Template:**

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Run command '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.10.12]
- Docker Version: [e.g., 24.0.5]

**Additional Context**
Any other relevant information.
```

### 2. **Suggesting Enhancements**

For feature requests or improvements:

- Check if the feature has already been requested
- Create an issue with the `enhancement` label
- Clearly describe the feature and its benefits
- Provide use cases and examples
- Discuss implementation approach if you have ideas

### 3. **Contributing Code**

We welcome code contributions! See the sections below for the workflow.

### 4. **Improving Documentation**

Documentation improvements are always appreciated:

- Fix typos or clarify existing docs
- Add examples and tutorials
- Improve setup instructions
- Translate documentation

### 5. **Helping Others**

- Answer questions in GitHub Discussions
- Review pull requests
- Help triage issues
- Share your experience using OSOrganicAI

---

## 🔄 Development Workflow

### 1. **Fork and Clone**

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/osorganicai.git
cd osorganicai

# Add upstream remote
git remote add upstream https://github.com/originalowner/osorganicai.git
```

### 2. **Set Up Development Environment**

Follow the [Setup Guide](setup.md) to configure your environment.

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. **Create a Branch**

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-number-description
```

**Branch Naming Conventions:**

- `feature/add-security-agent` — New features
- `bugfix/fix-webhook-handler` — Bug fixes
- `docs/improve-setup-guide` — Documentation
- `refactor/cleanup-agent-code` — Code refactoring
- `test/add-workflow-tests` — Test additions

### 4. **Make Your Changes**

```bash
# Make your code changes
# Follow the coding standards (see below)

# Add tests for your changes
# Update documentation if needed
```

### 5. **Test Your Changes**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Lint your code
black .
flake8 .
mypy src/

# Run pre-commit checks
pre-commit run --all-files
```

### 5a. **Validate with Test Child (CRITICAL for Template Changes)**

**If you're modifying base agents, templates, or core infrastructure**, you MUST validate using the internal test-child:

```bash
# Navigate to test-child
cd test-child/

# Set up test environment
cp ../.env.example .env.test
# Edit .env.test with test credentials

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# Run test-child locally
vercel dev

# Deploy to Vercel preview
vercel

# Test end-to-end
# 1. Create test issue in your test GitHub repo
# 2. Verify webhook triggers
# 3. Verify agents respond correctly
# 4. Check Supabase data
# 5. Verify deployment succeeds
```

**Validation Checklist:**
- [ ] test-child deploys successfully to Vercel
- [ ] Webhook receives and processes GitHub events
- [ ] Base agent changes work in test-child agents
- [ ] Database operations execute correctly
- [ ] No errors in Vercel function logs
- [ ] Test issue workflow completes successfully

**Why This Matters:** Template changes affect ALL child instances. The test-child validates your changes won't break downstream users.

### 6. **Commit Your Changes**

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add security agent for code scanning"
```

**Commit Message Guidelines:**

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(agent): add security agent for vulnerability scanning

Implements a new security agent that scans generated code for
common vulnerabilities using Bandit and safety checks.

Closes #42
```

```bash
fix(webhook): handle missing issue labels gracefully

Previously, the webhook handler would crash if an issue had no labels.
Now it defaults to an empty list.

Fixes #123
```

### 7. **Push to Your Fork**

```bash
# Push your branch
git push origin feature/your-feature-name
```

### 8. **Create a Pull Request**

1. Go to your fork on GitHub
2. Click **"New Pull Request"**
3. Select your feature branch
4. Fill out the PR template (see below)
5. Submit the pull request

**Pull Request Template:**

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
Closes #[issue number]

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All tests pass
- [ ] Added new tests for this change
- [ ] Updated documentation

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
```

### 9. **Respond to Feedback**

- Address reviewer comments
- Make requested changes
- Push updates to the same branch
- Re-request review when ready

```bash
# Make changes based on feedback
git add .
git commit -m "Address review feedback"
git push origin feature/your-feature-name
```

---

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length:** 100 characters (not 79)
- **Formatter:** Black (with default settings)
- **Linter:** Flake8
- **Type hints:** Use type hints for all functions
- **Docstrings:** Use Google-style docstrings

**Example:**

```python
from typing import List, Optional


class ProductOwnerAgent:
    """Manages requirements gathering and task refinement.

    The Product Owner Agent interacts with users through GitHub issues
    to clarify requirements and prepare tasks for the Developer Agent.

    Attributes:
        llm_client: Client for AI model interactions.
        github_client: Client for GitHub API operations.
        knowledge_base: Repository of project context and conventions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        github_client: GitHubClient,
        knowledge_base: Optional[KnowledgeBase] = None,
    ) -> None:
        """Initialize the Product Owner Agent.

        Args:
            llm_client: Client for AI model interactions.
            github_client: Client for GitHub API operations.
            knowledge_base: Optional knowledge base for context.
        """
        self.llm = llm_client
        self.github = github_client
        self.knowledge_base = knowledge_base or KnowledgeBase()

    def analyze_requirements(self, issue: Issue) -> RequirementAnalysis:
        """Analyze issue requirements and determine if clarification is needed.

        Args:
            issue: The GitHub issue to analyze.

        Returns:
            RequirementAnalysis containing clarity assessment and questions.

        Raises:
            ValueError: If issue content is empty or invalid.
        """
        if not issue.body:
            raise ValueError("Issue body cannot be empty")

        # Implementation here
        pass
```

### Code Organization

```python
# Standard library imports
import os
import sys
from typing import List, Optional

# Third-party imports
import requests
from langchain import LLMChain

# Local imports
from src.agents.base import BaseAgent
from src.utils.logger import get_logger
```

### Testing Standards

- **Coverage:** Aim for >80% code coverage
- **Naming:** Use descriptive test names (`test_product_owner_asks_clarifying_questions`)
- **Structure:** Arrange-Act-Assert pattern
- **Mocking:** Mock external services (GitHub API, AI models)

**Example:**

```python
import pytest
from unittest.mock import Mock, patch

from src.agents.product_owner import ProductOwnerAgent


class TestProductOwnerAgent:
    """Tests for Product Owner Agent."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock()

    @pytest.fixture
    def mock_github_client(self):
        """Create a mock GitHub client."""
        return Mock()

    @pytest.fixture
    def agent(self, mock_llm_client, mock_github_client):
        """Create a Product Owner Agent instance."""
        return ProductOwnerAgent(mock_llm_client, mock_github_client)

    def test_analyze_requirements_with_clear_issue(self, agent):
        """Test analysis of a clear, well-defined issue."""
        # Arrange
        issue = Mock(body="Add user authentication with JWT tokens")

        # Act
        result = agent.analyze_requirements(issue)

        # Assert
        assert result.is_complete is True
        assert len(result.questions) == 0

    def test_analyze_requirements_with_vague_issue(self, agent):
        """Test analysis of a vague issue requiring clarification."""
        # Arrange
        issue = Mock(body="Make the app better")

        # Act
        result = agent.analyze_requirements(issue)

        # Assert
        assert result.needs_clarification is True
        assert len(result.questions) > 0
```

---

## 🏗️ Template-Specific Guidelines

### Contributing to Base Agent Classes

When modifying `src/agents/base.py` or generic agent scaffolds:

1. **Keep It Generic**: Don't add domain-specific logic to base classes
2. **Provide Extension Points**: Use methods like `get_domain_context()` for child customization
3. **Maintain Backward Compatibility**: Avoid breaking changes
4. **Document Extension Points**: Clearly explain how children should override methods
5. **Test with test-child**: Validate that specialization works

**Example of Good Base Agent Design:**
```python
# src/agents/base.py
class BaseAgent:
    """Generic agent scaffold for all child instances."""

    def log_action(self, action_type: str, payload: dict) -> None:
        """All children inherit this logging behavior."""
        self.supabase.table('agent_actions').insert({
            'agent_type': self.__class__.__name__,
            'action_type': action_type,
            'payload': payload
        }).execute()

    def get_domain_context(self) -> str:
        """Override in child instances for domain-specific context.

        Returns:
            Empty string in base class, domain context in children.
        """
        return ""  # Children override this

    def analyze_issue(self, issue_text: str) -> AnalysisResult:
        """Analyze issue with optional domain context."""
        # Generic analysis logic
        base_prompt = self._build_base_prompt(issue_text)

        # Extension point: add domain context
        domain_context = self.get_domain_context()
        if domain_context:
            base_prompt += f"\n\nDomain Context:\n{domain_context}"

        return self.llm.analyze(base_prompt)
```

### Contributing to Templates

When adding to `templates/`:

1. **Keep Templates Minimal**: Provide structure, not implementation
2. **Use Placeholders**: Allow easy customization (e.g., `{{PROJECT_NAME}}`)
3. **Document Template Variables**: Explain what each placeholder does
4. **Test Template Generation**: Verify templates can spawn valid children

### Backward Compatibility Requirements

**CRITICAL**: Template changes must not break existing child instances.

**Breaking Changes** (avoid if possible):
- Removing methods from BaseAgent
- Changing method signatures
- Removing required environment variables
- Changing database schema without migration

**Non-Breaking Changes** (preferred):
- Adding new optional methods
- Adding new extension points
- Adding new environment variables with defaults
- Deprecating with warnings before removing

**If You Must Break Compatibility:**
1. Discuss in GitHub issue first
2. Provide migration guide
3. Bump major version number
4. Announce in release notes
5. Give advance warning to community

### Project Structure Guidelines

### Adding New Agents

1. Create agent class in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods with extension points
4. Add tests in `tests/test_agents.py`
5. Test specialization in `test-child/`
6. Document in `docs/architecture.md`

### Adding New Workflows

1. Create workflow in `src/workflows/`
2. Keep workflows generic and reusable
3. Define clear entry and exit points
4. Add integration tests
5. Update workflow documentation

### Adding New Dependencies

```bash
# Install the package
pip install new-package

# Add to requirements.txt
pip freeze | grep new-package >> requirements.txt

# Or manually edit requirements.txt with pinned version
echo "new-package==1.2.3" >> requirements.txt

# Consider impact on child instances
# - Will children need this dependency?
# - Is it truly necessary for the template?
# - Could it be optional?
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::TestProductOwnerAgent::test_analyze_requirements

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

### Writing Tests

- Write tests for new features and bug fixes
- Test edge cases and error conditions
- Use fixtures for common setup
- Mock external dependencies
- Keep tests fast and isolated

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_full_workflow_integration():
    """Slow test that runs full workflow."""
    pass

@pytest.mark.unit
def test_agent_function():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_github_api_integration():
    """Integration test with external service."""
    pass
```

---

## 📚 Documentation Guidelines

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep docstrings up to date with code changes

### User Documentation

- Write in clear, simple language
- Include examples and code snippets
- Add screenshots where helpful
- Test all commands and instructions

---

## 🔍 Review Process

### What We Look For

- **Functionality:** Does it work as intended?
- **Tests:** Are there adequate tests?
- **Code quality:** Is it clean, readable, maintainable?
- **Documentation:** Is it well-documented?
- **Performance:** Does it perform efficiently?
- **Security:** Does it introduce vulnerabilities?

### Review Checklist

Reviewers will check:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Commits are clear and well-organized
- [ ] PR description is complete
- [ ] No security issues introduced

---

## 🏷️ Issue and PR Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to docs |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `question` | Further information requested |
| `wontfix` | This will not be worked on |
| `duplicate` | This issue or PR already exists |
| `dependencies` | Pull requests that update a dependency |

---

## 🚀 Release Process & Template Versioning

### Mother Repository Releases

Releases are managed by project maintainers:

1. **Version Bump**: Update version in `setup.py` or `pyproject.toml`
2. **Update CHANGELOG.md**: Document all changes with migration notes if needed
3. **Test with test-child**: Ensure validation passes
4. **Create Git Tag**: `git tag v1.2.0`
5. **GitHub Release**: Create release with comprehensive notes
6. **Announce**: Notify community in Discussions

### Semantic Versioning for Templates

We use semantic versioning with template-specific semantics:

**Major Version (x.0.0) - Breaking Changes**
- Changes that break existing child instances
- Removed BaseAgent methods
- Changed method signatures
- Database schema changes requiring migration

**Minor Version (0.x.0) - New Features**
- New agent types
- New extension points
- New optional features
- Backward-compatible enhancements

**Patch Version (0.0.x) - Bug Fixes**
- Bug fixes in base agents
- Documentation corrections
- Test improvements
- Performance optimizations

### Migration Guides

For major versions, include migration guide in release notes:

```markdown
## Migrating from v1.x to v2.0

### Breaking Changes
1. `BaseAgent.old_method()` removed → Use `BaseAgent.new_method()` instead
2. Environment variable `OLD_VAR` renamed to `NEW_VAR`

### Migration Steps
1. Update your agents:
   ```python
   # Old
   result = agent.old_method()

   # New
   result = agent.new_method()
   ```
2. Update your `.env`:
   ```bash
   # OLD_VAR=value
   NEW_VAR=value
   ```
3. Run database migration (if applicable)
4. Test thoroughly before deploying
```

### Child Instance Update Strategy

Child instances can opt-in to template updates:

```bash
# In child instance repository
git remote add template https://github.com/org/osorganicai.git
git fetch template
git merge template/v2.0.0  # Specific version
```

---

## 💡 Tips for Contributors

### For Beginners

- Start with `good first issue` labeled issues
- Read the documentation thoroughly
- Ask questions in GitHub Discussions
- Join the community and introduce yourself

### For Experienced Contributors

- Help review PRs
- Mentor new contributors
- Tackle complex issues
- Improve architecture and design

### Template-Specific Tips

- **Think Generic**: When adding features, ask "Can all child instances use this?"
- **Test with test-child**: Always validate template changes with the internal test instance
- **Avoid Domain Logic**: Keep base agents domain-agnostic
- **Document Extension Points**: Make it clear how children should customize
- **Consider Impact**: Template changes affect many downstream projects

### General Tips

- **Communicate early:** Discuss major changes before implementing
- **Keep PRs focused:** One feature or fix per PR
- **Be patient:** Reviews may take time
- **Be responsive:** Address feedback promptly
- **Have fun:** Enjoy the process!

---

## 📞 Getting Help

If you need help:

1. **Read the docs:** Check [setup.md](setup.md) and [architecture.md](architecture.md)
2. **Search issues:** Someone may have had the same question
3. **Ask in Discussions:** Use GitHub Discussions for questions
4. **Join community:** Connect with other contributors

---

## 🙏 Recognition

Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Credited in documentation they improve

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to OSOrganicAI! Together, we're building the **meta-template** that powers autonomous software development across countless child instances. Your contributions help teams worldwide spawn and run AI-driven development systems. 🚀

**Remember**: When you improve the mother repository, you're improving the foundation for all current and future child instances. Make it count!

---

**Key Resources for Template Contributors:**
- [Architectural Vision](vision.md) - Understand the meta-template concept
- [Template Usage Guide](template-usage.md) - See how children use the template
- [Setup Guide](setup.md) - Test child setup instructions
- [Architecture Documentation](architecture.md) - Template layers and delegation
