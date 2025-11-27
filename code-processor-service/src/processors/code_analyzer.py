"""
Code analyzer for repository analysis.

This module provides functionality to analyze code using LLM
to extract insights, summaries, and recommendations.
"""

from typing import Any, TYPE_CHECKING
from langchain_core.messages import HumanMessage, SystemMessage

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
        llm_client: "AzureOpenAIClient",
        issues: dict[str, Any],
        mcp_client: Any
    ) -> dict[str, Any]:
        """
        Analyze repository code and generate insights.
        
        Args:
            repository: Repository information dictionary
            metadata: Extracted metadata dictionary
            llm_client: Azure OpenAI client
            issues: GitHub issues data
            mcp_client: MCP client to fetch actual code
            
        Returns:
            Analysis result with summary, insights, and recommendations
        """
        # Prepare analysis input
        file_list = metadata.get("files", [])
        dependencies = metadata.get("dependencies", [])
        tech_stack = metadata.get("tech_stack", [])
        code_metrics = metadata.get("code_metrics", {})
        services = metadata.get("services", [])
        
        # Generate summary using LLM
        summary_result = await llm_client.summarize_repository(
            repo_info=repository,
            file_structure=file_list,
            readme_content=repository.get("readme")
        )
        
        # Analyze services with actual code (enterprise-level)
        analyzed_services = []
        if services and mcp_client:
            print(f"\n=== ANALYZING {len(services)} SERVICES ===")
            analyzed_services = await self._analyze_services(
                services, 
                repository.get("owner"), 
                repository.get("name"),
                mcp_client,
                llm_client
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
            ),
            "services": analyzed_services
        }
        
        return analysis

    async def _analyze_services(
        self,
        services: list[dict[str, Any]],
        owner: str,
        repo: str,
        mcp_client: Any,
        llm_client: "AzureOpenAIClient"
    ) -> list[dict[str, Any]]:
        """Analyze services by fetching and examining actual code."""
        analyzed = []
        
        for service in services:
            service_name = service.get("name")
            service_path = f"src/{service_name}"
            
            print(f"\nAnalyzing service: {service_name}")
            
            # Fetch actual files from the service
            service_files = await mcp_client.get_service_files(
                owner, repo, service_path, max_files=10
            )
            
            if service_files:
                print(f"  Fetched {len(service_files)} files: {[f['name'] for f in service_files]}")
                
                # Let LLM analyze the actual code
                analysis = await self._llm_analyze_service(
                    service_name,
                    service_files,
                    service.get("file_extensions", []),
                    service.get("dependencies", []),
                    llm_client
                )
                
                analyzed.append({
                    **service,
                    "description": analysis.get("description", ""),
                    "technologies": analysis.get("technologies", []),
                    "type": analysis.get("type", service.get("type", "service"))
                })
            else:
                # No files fetched, use basic info
                analyzed.append(service)
        
        return analyzed

    async def _llm_analyze_service(
        self,
        service_name: str,
        files: list[dict[str, Any]],
        file_extensions: list[str],
        dependencies: list[str],
        llm_client: "AzureOpenAIClient"
    ) -> dict[str, Any]:
        """Use LLM to analyze service from actual code files."""
        # Build context from actual files
        files_context = []
        for file in files[:8]:
            files_context.append(f"File: {file['name']}\n```\n{file['content'][:1000]}\n```")
        
        prompt = f"""Analyze this microservice from its actual source code and return ONLY valid JSON.

Service Name: {service_name}
File Extensions: {', '.join(file_extensions)}
Dependencies: {', '.join(dependencies[:10])}

Actual Code Files:
{chr(10).join(files_context)}

Return ONLY this JSON structure (no markdown, no explanation):
{{
  "description": "Detailed technical description (700-900 chars) of what this service does",
  "technologies": ["list", "of", "technologies"],
  "type": "api or webapp or worker or library or service"
}}"""

        try:
            response = await llm_client._client.ainvoke([
                SystemMessage(content="You are an expert software architect. Return ONLY valid JSON, no markdown formatting."),
                HumanMessage(content=prompt)
            ])
            
            import json
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"  LLM analysis failed: {str(e)}")
            return {
                "description": f"{service_name} service",
                "technologies": [],
                "type": "service"
            }

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
