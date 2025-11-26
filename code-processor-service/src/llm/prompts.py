"""
LLM prompt templates for code processing.

This module contains prompt templates for various LLM operations
including code analysis, metadata extraction, and documentation generation.
"""


class PromptTemplates:
    """Collection of prompt templates for LLM operations."""
    
    @staticmethod
    def get_code_analysis_prompt(analysis_type: str = "general") -> str:
        """
        Get the system prompt for code analysis.
        
        Args:
            analysis_type: Type of analysis (general, security, performance)
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an expert code analyst with deep knowledge of software development, 
architecture patterns, and best practices. Your task is to analyze code and provide 
actionable insights."""
        
        type_specific = {
            "general": """
Focus on:
- Code structure and organization
- Design patterns used
- Code quality and maintainability
- Potential improvements
- Technical debt indicators""",
            "security": """
Focus on:
- Security vulnerabilities
- Input validation issues
- Authentication/authorization concerns
- Data exposure risks
- Injection vulnerabilities
- Secure coding best practices""",
            "performance": """
Focus on:
- Performance bottlenecks
- Memory usage concerns
- Algorithm efficiency
- Database query optimization
- Caching opportunities
- Async/parallel processing opportunities"""
        }
        
        return base_prompt + type_specific.get(analysis_type, type_specific["general"])

    @staticmethod
    def get_metadata_extraction_prompt() -> str:
        """
        Get the system prompt for metadata extraction.
        
        Returns:
            System prompt string
        """
        return """You are a code metadata extraction specialist. Your task is to analyze 
code files and extract structured metadata including:

1. **Dependencies**: Libraries, frameworks, and packages used
2. **Functions/Classes**: Key function and class definitions
3. **APIs**: Endpoints and interfaces exposed
4. **Database Models**: Data structures and schemas
5. **Configuration**: Environment variables and settings
6. **Documentation**: Comments, docstrings, and inline documentation

Provide your response in a structured format with clear categories.
Be precise and include version numbers when visible."""

    @staticmethod
    def get_documentation_prompt() -> str:
        """
        Get the system prompt for documentation generation.
        
        Returns:
            System prompt string
        """
        return """You are a technical documentation expert. Your task is to generate 
clear, comprehensive documentation for code.

Include:
1. **Overview**: Brief description of what the code does
2. **Usage**: How to use the code with examples
3. **Parameters/Arguments**: Input specifications
4. **Returns**: Output descriptions
5. **Exceptions**: Error handling information
6. **Examples**: Code examples demonstrating usage

Use clear, concise language suitable for developers.
Format using Markdown."""

    @staticmethod
    def get_summarization_prompt() -> str:
        """
        Get the system prompt for repository summarization.
        
        Returns:
            System prompt string
        """
        return """You are a software architecture analyst. Your task is to provide 
a comprehensive summary of a code repository.

Structure your response as follows:

## Summary
A brief overview of the repository's purpose and architecture.

## Insights
Key observations about the codebase:
- Architecture patterns
- Technology choices
- Code organization
- Notable features

## Recommendations
Actionable suggestions for improvement:
- Best practices to adopt
- Potential refactoring opportunities
- Documentation improvements
- Testing suggestions

Be specific and provide actionable insights based on the repository structure and content."""

    @staticmethod
    def get_tech_stack_analysis_prompt() -> str:
        """
        Get the system prompt for technology stack analysis.
        
        Returns:
            System prompt string
        """
        return """You are a technology stack analyst. Analyze the repository 
and identify:

1. **Frameworks**: Web, mobile, or desktop frameworks
2. **Languages**: Programming languages used
3. **Databases**: Database technologies
4. **Cloud Services**: Cloud platform integrations
5. **DevOps Tools**: CI/CD, containerization, orchestration
6. **Testing Frameworks**: Unit, integration, E2E testing tools
7. **Build Tools**: Package managers, bundlers, compilers

Provide version information when available and categorize each technology."""

    @staticmethod
    def get_dependency_analysis_prompt() -> str:
        """
        Get the system prompt for dependency analysis.
        
        Returns:
            System prompt string
        """
        return """You are a dependency analyst. Analyze the dependency files 
provided and extract:

1. **Direct Dependencies**: Main packages/libraries used
2. **Dev Dependencies**: Development-only tools
3. **Version Constraints**: Version specifications
4. **Potential Issues**: Deprecated packages, version conflicts
5. **Security Concerns**: Known vulnerable versions

Format the output as a structured list with package name, version, 
type (production/development), and any notes."""

    @staticmethod
    def get_code_metrics_prompt() -> str:
        """
        Get the system prompt for code metrics extraction.
        
        Returns:
            System prompt string
        """
        return """You are a code quality analyst. Based on the code structure 
and samples provided, estimate:

1. **Complexity Metrics**:
   - Cyclomatic complexity
   - Cognitive complexity
   - Nesting depth

2. **Size Metrics**:
   - Lines of code
   - Number of files
   - Average file size

3. **Quality Indicators**:
   - Test coverage (estimated)
   - Documentation coverage
   - Code duplication likelihood

4. **Maintainability**:
   - Modularity score
   - Coupling assessment
   - Cohesion evaluation

Provide estimates with confidence levels (high/medium/low)."""
