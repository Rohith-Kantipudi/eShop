"""
Azure OpenAI client for GPT-4o integration.

This module provides a client for interacting with Azure OpenAI services,
specifically configured for GPT-4o model usage.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


class AzureOpenAIClient:
    """
    Client for Azure OpenAI GPT-4o integration.
    
    This client handles authentication, configuration, and
    interaction with Azure OpenAI services for code analysis.
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL. Reads from 
                     AZURE_OPENAI_ENDPOINT if not provided.
            api_key: Azure OpenAI API key. Reads from 
                    AZURE_OPENAI_API_KEY if not provided.
            deployment: Model deployment name. Reads from 
                       AZURE_OPENAI_DEPLOYMENT if not provided.
            api_version: API version. Reads from 
                        AZURE_OPENAI_API_VERSION if not provided.
        """
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.api_version = api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
        )
        
        self._validate_config()
        self._client = self._create_client()

    def _validate_config(self) -> None:
        """Validate that required configuration is present."""
        if not self.endpoint:
            raise ValueError(
                "Azure OpenAI endpoint is required. "
                "Set AZURE_OPENAI_ENDPOINT environment variable."
            )
        if not self.api_key:
            raise ValueError(
                "Azure OpenAI API key is required. "
                "Set AZURE_OPENAI_API_KEY environment variable."
            )

    def _create_client(self) -> AzureChatOpenAI:
        """Create the LangChain Azure ChatOpenAI client."""
        return AzureChatOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            azure_deployment=self.deployment,
            api_version=self.api_version,
            temperature=0.1,
            max_tokens=4096
        )

    async def analyze_code(
        self,
        code: str,
        context: str = "",
        analysis_type: str = "general"
    ) -> str:
        """
        Analyze code using GPT-4o.
        
        Args:
            code: Code snippet to analyze
            context: Additional context about the code
            analysis_type: Type of analysis (general, security, performance)
            
        Returns:
            Analysis result as string
        """
        from .prompts import PromptTemplates
        
        system_prompt = PromptTemplates.get_code_analysis_prompt(analysis_type)
        user_prompt = f"""
Context: {context}

Code:
```
{code}
```

Please analyze this code and provide insights.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await self._client.ainvoke(messages)
        return response.content

    async def extract_metadata(
        self,
        file_contents: dict[str, str],
        file_types: list[str]
    ) -> dict[str, Any]:
        """
        Extract metadata from code files using GPT-4o.
        
        Args:
            file_contents: Dictionary of file paths to contents
            file_types: List of file types in the repository
            
        Returns:
            Extracted metadata dictionary
        """
        from .prompts import PromptTemplates
        
        # Prepare a summary of files
        files_summary = "\n".join([
            f"- {path}: {len(content)} bytes"
            for path, content in file_contents.items()
        ])
        
        system_prompt = PromptTemplates.get_metadata_extraction_prompt()
        user_prompt = f"""
File types in repository: {', '.join(file_types)}

Files:
{files_summary}

Sample file contents (first 3 files):
"""
        # Add sample contents
        for i, (path, content) in enumerate(file_contents.items()):
            if i >= 3:
                break
            user_prompt += f"\n\n--- {path} ---\n{content[:2000]}"
        
        user_prompt += "\n\nPlease extract metadata from these files."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await self._client.ainvoke(messages)
        
        # Parse response to structured format
        return self._parse_metadata_response(response.content)

    async def generate_documentation(
        self,
        code: str,
        file_path: str
    ) -> str:
        """
        Generate documentation for code.
        
        Args:
            code: Code to document
            file_path: Path of the file
            
        Returns:
            Generated documentation
        """
        from .prompts import PromptTemplates
        
        system_prompt = PromptTemplates.get_documentation_prompt()
        user_prompt = f"""
File: {file_path}

Code:
```
{code}
```

Please generate comprehensive documentation for this code.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await self._client.ainvoke(messages)
        return response.content

    async def summarize_repository(
        self,
        repo_info: dict[str, Any],
        file_structure: list[dict],
        readme_content: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generate an intelligent summary of the repository.
        
        Args:
            repo_info: Repository information
            file_structure: List of files in the repository
            readme_content: Optional README content
            
        Returns:
            Summary with insights and recommendations
        """
        from .prompts import PromptTemplates
        
        # Create file structure overview
        file_overview = "\n".join([
            f["path"] for f in file_structure[:100]  # Limit to 100 files
        ])
        
        system_prompt = PromptTemplates.get_summarization_prompt()
        user_prompt = f"""
Repository: {repo_info.get('name')}
Owner: {repo_info.get('owner')}
Description: {repo_info.get('description', 'N/A')}
Languages: {', '.join(repo_info.get('languages', []))}

File Structure (up to 100 files):
{file_overview}

README Content:
{readme_content[:3000] if readme_content else 'No README available'}

Please provide a comprehensive summary with insights and recommendations.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await self._client.ainvoke(messages)
        
        return self._parse_summary_response(response.content)

    def _parse_metadata_response(self, response: str) -> dict[str, Any]:
        """Parse LLM response into structured metadata."""
        # Basic parsing - in production, use more robust parsing
        return {
            "raw_analysis": response,
            "extracted_at": "auto"
        }

    def _parse_summary_response(self, response: str) -> dict[str, Any]:
        """Parse LLM response into structured summary."""
        # Parse the response into summary, insights, and recommendations
        lines = response.split("\n")
        
        summary = ""
        insights = []
        recommendations = []
        
        current_section = "summary"
        
        for line in lines:
            line_lower = line.lower()
            if "insight" in line_lower:
                current_section = "insights"
                continue
            elif "recommendation" in line_lower:
                current_section = "recommendations"
                continue
            
            if line.strip():
                if current_section == "summary":
                    summary += line + " "
                elif current_section == "insights":
                    if line.strip().startswith(("-", "*", "•")):
                        insights.append(line.strip()[1:].strip())
                elif current_section == "recommendations":
                    if line.strip().startswith(("-", "*", "•")):
                        recommendations.append(line.strip()[1:].strip())
        
        return {
            "summary": summary.strip() or response[:500],
            "insights": insights or ["Repository analysis completed"],
            "recommendations": recommendations or ["Review generated metadata for accuracy"]
        }

    async def invoke_with_streaming(
        self,
        prompt: str,
        system_prompt: str = ""
    ):
        """
        Invoke the model with streaming support.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Yields:
            Streamed response chunks
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        async for chunk in self._client.astream(messages):
            yield chunk.content
