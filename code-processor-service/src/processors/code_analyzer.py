"""
Code analyzer for repository analysis.

This module provides functionality to analyze code using LLM
to extract insights, summaries, and recommendations.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..llm import AzureOpenAIClient


class CodeAnalyzer:
    """
    Analyzes code using LLM to generate insights.
    
    This class uses Azure OpenAI GPT-4o to analyze repository
    code and generate summaries, insights, and recommendations.
    """
    
    async def analyze(
        self,
        repository: dict[str, Any],
        metadata: dict[str, Any],
        llm_client: "AzureOpenAIClient"
    ) -> dict[str, Any]:
        """
        Analyze repository code and generate insights.
        
        Args:
            repository: Repository information dictionary
            metadata: Extracted metadata dictionary
            llm_client: Azure OpenAI client
            
        Returns:
            Analysis result with summary, insights, and recommendations
        """
        # Prepare analysis input
        file_list = metadata.get("files", [])
        dependencies = metadata.get("dependencies", [])
        tech_stack = metadata.get("tech_stack", [])
        code_metrics = metadata.get("code_metrics", {})
        
        # Generate summary using LLM
        summary_result = await llm_client.summarize_repository(
            repo_info=repository,
            file_structure=file_list,
            readme_content=repository.get("readme")
        )
        
        # Enhance with code metrics analysis
        analysis = {
            "summary": summary_result.get("summary", self._generate_fallback_summary(
                repository, code_metrics
            )),
            "insights": summary_result.get("insights", []) + self._generate_code_insights(
                code_metrics, tech_stack
            ),
            "recommendations": summary_result.get("recommendations", []) + self._generate_recommendations(
                metadata
            )
        }
        
        return analysis

    def _generate_fallback_summary(
        self,
        repository: dict[str, Any],
        code_metrics: dict[str, Any]
    ) -> str:
        """Generate a fallback summary when LLM is unavailable."""
        repo_name = repository.get("name", "Unknown")
        owner = repository.get("owner", "Unknown")
        description = repository.get("description", "No description available")
        languages = repository.get("languages", [])
        total_files = code_metrics.get("total_files", 0)
        
        return (
            f"{repo_name} is a repository owned by {owner}. "
            f"{description}. "
            f"The repository contains {total_files} files "
            f"primarily written in {', '.join(languages[:3]) if languages else 'various languages'}."
        )

    def _generate_code_insights(
        self,
        code_metrics: dict[str, Any],
        tech_stack: list[dict[str, Any]]
    ) -> list[str]:
        """Generate insights from code metrics."""
        insights = []
        
        total_files = code_metrics.get("total_files", 0)
        languages = code_metrics.get("languages_breakdown", {})
        
        # File count insight
        if total_files > 1000:
            insights.append(
                f"Large codebase with {total_files} files - "
                "consider modularization for maintainability"
            )
        elif total_files > 100:
            insights.append(
                f"Medium-sized codebase with {total_files} files"
            )
        else:
            insights.append(
                f"Compact codebase with {total_files} files"
            )
        
        # Language diversity insight
        if len(languages) > 5:
            insights.append(
                f"Multi-language project using {len(languages)} languages - "
                "ensure consistent coding standards across languages"
            )
        
        # Primary language insight
        if languages:
            primary_lang = max(languages.items(), key=lambda x: x[1])
            insights.append(
                f"Primary language is {primary_lang[0]} "
                f"({primary_lang[1]} files)"
            )
        
        # Tech stack insights
        frameworks = [t for t in tech_stack if t.get("category") == "framework"]
        if frameworks:
            framework_names = [f.get("name") for f in frameworks]
            insights.append(
                f"Uses frameworks: {', '.join(framework_names)}"
            )
        
        return insights

    def _generate_recommendations(
        self,
        metadata: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on metadata."""
        recommendations = []
        
        files = metadata.get("files", [])
        dependencies = metadata.get("dependencies", [])
        
        # Check for documentation
        doc_files = [f for f in files if f.get("extension") in [".md", ".rst", ".txt"]]
        if len(doc_files) < 5:
            recommendations.append(
                "Consider adding more documentation files "
                "to improve project accessibility"
            )
        
        # Check for tests
        test_files = [
            f for f in files 
            if "test" in f.get("path", "").lower() or 
               "spec" in f.get("path", "").lower()
        ]
        if not test_files:
            recommendations.append(
                "No test files detected - consider adding unit tests"
            )
        
        # Check dependencies for outdated patterns
        old_dependencies = [
            d for d in dependencies 
            if d.get("version") and "^0." in str(d.get("version", ""))
        ]
        if old_dependencies:
            recommendations.append(
                f"Found {len(old_dependencies)} dependencies with 0.x versions - "
                "review for stability"
            )
        
        # CI/CD recommendation
        ci_files = [
            f for f in files 
            if ".github/workflows" in f.get("path", "") or 
               f.get("name") in [".travis.yml", "azure-pipelines.yml"]
        ]
        if not ci_files:
            recommendations.append(
                "Consider setting up CI/CD pipelines for automated testing"
            )
        
        return recommendations

    async def analyze_specific_file(
        self,
        file_content: str,
        file_path: str,
        llm_client: "AzureOpenAIClient",
        analysis_type: str = "general"
    ) -> dict[str, Any]:
        """
        Analyze a specific file.
        
        Args:
            file_content: Content of the file
            file_path: Path to the file
            llm_client: Azure OpenAI client
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis result for the specific file
        """
        analysis = await llm_client.analyze_code(
            code=file_content,
            context=f"File: {file_path}",
            analysis_type=analysis_type
        )
        
        return {
            "file_path": file_path,
            "analysis": analysis,
            "analysis_type": analysis_type
        }
