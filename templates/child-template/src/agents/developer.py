"""
Domain-Specialized Developer Agent for CHILD_TEMPLATE.

TODO: Customize this agent for your tech stack by:
1. Replacing CHILD_TEMPLATE with your project name
2. Updating get_domain_context() with your tech stack and code patterns
3. (Optional) Customizing customize_prompt() for extra code generation guidance

This agent inherits from the mother repository's DeveloperAgent
and adds tech stack specific code generation patterns.
"""

from typing import Optional, List, Dict, Any

# Import the mother repository's base Developer Agent
import sys
from pathlib import Path

# Add parent directory to path to import from mother repo
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.agents.developer import DeveloperAgent as BaseDeveloperAgent


class DeveloperAgent(BaseDeveloperAgent):
    """
    Domain-specialized Developer Agent.

    TODO: Update this docstring with your tech stack.

    This agent inherits all core functionality from the mother repository's
    DeveloperAgent but adds [YOUR TECH STACK] specific code patterns and
    development considerations.

    **[YOUR DOMAIN] Specialization:**
    TODO: List your tech stack here, for example:
    - Language: Python/TypeScript/Go
    - Framework: FastAPI/Next.js/Express
    - Database: Supabase/PostgreSQL/MongoDB
    - Key Libraries: [Your dependencies]

    **Extension Pattern:**
    - get_domain_context(): Defines tech stack and code patterns
    - All other methods inherited without modification
    """

    def get_domain_context(self) -> str:
        """
        Get tech stack and code patterns for this agent.

        TODO: Replace this placeholder with your actual tech stack.

        Returns:
            str: Tech stack context string

        Example for a TypeScript/Next.js stack:
            return '''
            ## Tech Stack

            - Language: TypeScript 5.0+
            - Framework: Next.js 14 (App Router)
            - Database: Prisma + PostgreSQL
            - API: tRPC for type-safe APIs

            ### Code Patterns:
            [Show examples of your models, API routes, etc.]
            '''
        """
        return """
## YOUR DOMAIN Tech Stack Context

TODO: Replace this with your actual tech stack and code patterns.

You are generating code for a [YOUR DOMAIN] application with the following tech stack:

### Backend:
- **Language**: [Your language and version]
- **Framework**: [Your framework]
- **Database**: [Your database]
- **ORM/Query Builder**: [If applicable]
- **Authentication**: [Your auth solution]
- **Deployment**: [Your deployment platform]

### Code Patterns:

#### 1. Data Models
TODO: Provide examples of your data models

```[language]
# Example model structure
class YourModel:
    id: str
    field1: type
    field2: type
```

#### 2. API Endpoints
TODO: Provide examples of your API patterns

```[language]
# Example API endpoint structure
@router.get("/api/resource")
async def get_resource():
    # Implementation
    pass
```

#### 3. Database Queries
TODO: Show how to query your database

```[language]
# Example database query
result = db.query(...)
```

#### 4. Testing Patterns
TODO: Show your testing patterns

```[language]
# Example test structure
def test_feature():
    # Arrange
    # Act
    # Assert
    pass
```

### [YOUR DOMAIN] Specific Considerations:

#### Security:
TODO: Add security guidelines for your domain
- [Security concern 1]
- [Security concern 2]

#### Data Integrity:
TODO: Add data integrity considerations
- [Consideration 1]
- [Consideration 2]

#### Performance:
TODO: Add performance guidelines
- [Performance tip 1]
- [Performance tip 2]

#### Error Handling:
TODO: Add error handling patterns
- [Pattern 1]
- [Pattern 2]

### File Organization:
TODO: Define your project structure
```
src/
├── models/      # Data models
├── services/    # Business logic
├── api/         # API endpoints
└── utils/       # Utilities
```

### Code Quality Standards:
- **Type hints/annotations**: [Your approach]
- **Documentation**: [Your documentation style]
- **Testing**: [Your testing requirements]
- **Error handling**: [Your error handling approach]

When generating code:
1. Follow the patterns above
2. Include comprehensive error handling
3. Write tests alongside implementation
4. Consider edge cases
5. Add clear comments explaining business logic

---
💡 **Tip**: Look at test-child/src/agents/developer.py for a complete FastAPI/Supabase example.
"""

    def customize_prompt(self, base_prompt: str) -> str:
        """
        Customize prompts with tech-stack specific instructions.

        TODO: (Optional) Add extra code generation guidance.

        Args:
            base_prompt: Base prompt from parent class

        Returns:
            str: Customized prompt
        """
        customization = """

## [YOUR DOMAIN] Development Guidelines:

TODO: Add specific development guidelines for your domain.

### [Key Technology] Integration:
- [Guideline 1]
- [Guideline 2]

### [Common Pattern] Implementation:
- [Step 1]
- [Step 2]

### Testing Requirements:
- [Test type 1]
- [Test type 2]

### Code Structure:
- [Structural requirement 1]
- [Structural requirement 2]
"""
        return base_prompt + customization


# Verification code (for testing)
if __name__ == "__main__":
    print("✅ Developer Agent template loaded")
    print("\n⚠️  TODO: Customize get_domain_context() with your tech stack")
    print("\nTech Stack Context Preview:")
    agent_class = DeveloperAgent
    context = agent_class.get_domain_context(agent_class)

    if "TODO" in context:
        print("❌ Tech stack context still contains TODOs - needs customization!")
    else:
        print("✅ Tech stack context has been customized")

    print(f"\nContext length: {len(context)} characters")
