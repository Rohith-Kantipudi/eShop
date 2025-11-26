"""
Code Processor Service - Main entry point.

This module provides the main entry point for the Code Processor Service,
which uses LangGraph to extract and process metadata from GitHub repositories.
"""

import asyncio
import json
import os
from typing import Any, Optional

from dotenv import load_dotenv

from .graph import CodeProcessorWorkflow
from .mcp import GitHubMCPClient
from .llm import AzureOpenAIClient
from .processors import MetadataExtractor, CodeAnalyzer, JsonFormatter

# Load environment variables
load_dotenv()


class CodeProcessorService:
    """
    Main service for processing repository code metadata.
    
    This service uses LangGraph to orchestrate the extraction and
    processing of metadata from GitHub repositories using Azure OpenAI
    GPT-4o for intelligent analysis.
    """
    
    def __init__(
        self,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
        github_token: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None
    ):
        """
        Initialize the Code Processor Service.
        
        Args:
            repo_owner: Repository owner. Reads from REPOSITORY_OWNER env var if not provided.
            repo_name: Repository name. Reads from REPOSITORY_NAME env var if not provided.
            github_token: GitHub token. Reads from GITHUB_TOKEN env var if not provided.
            azure_endpoint: Azure OpenAI endpoint. Reads from env if not provided.
            azure_api_key: Azure OpenAI API key. Reads from env if not provided.
            azure_deployment: Azure OpenAI deployment name. Reads from env if not provided.
        """
        self.repo_owner = repo_owner or os.getenv("REPOSITORY_OWNER")
        self.repo_name = repo_name or os.getenv("REPOSITORY_NAME")
        
        if not self.repo_owner or not self.repo_name:
            raise ValueError(
                "Repository owner and name are required. "
                "Set REPOSITORY_OWNER and REPOSITORY_NAME environment variables "
                "or pass them as parameters."
            )
        
        # Initialize clients
        self.mcp_client = GitHubMCPClient(github_token=github_token)
        self.llm_client = AzureOpenAIClient(
            endpoint=azure_endpoint,
            api_key=azure_api_key,
            deployment=azure_deployment
        )
        
        # Initialize processors
        self.metadata_extractor = MetadataExtractor()
        self.code_analyzer = CodeAnalyzer()
        self.json_formatter = JsonFormatter()
        
        # Initialize workflow
        self.workflow = CodeProcessorWorkflow(
            mcp_client=self.mcp_client,
            llm_client=self.llm_client,
            metadata_extractor=self.metadata_extractor,
            code_analyzer=self.code_analyzer,
            json_formatter=self.json_formatter
        )

    async def process(self) -> "ProcessorResult":
        """
        Run the processing workflow.
        
        Returns:
            ProcessorResult containing the final state and JSON output
        """
        # Execute the workflow
        final_state = await self.workflow.process(
            self.repo_owner,
            self.repo_name
        )
        
        return ProcessorResult(final_state)

    async def process_with_options(
        self,
        include_file_contents: bool = False,
        max_files: int = 500,
        analysis_types: Optional[list[str]] = None
    ) -> "ProcessorResult":
        """
        Run the processing workflow with custom options.
        
        Args:
            include_file_contents: Whether to include file content previews
            max_files: Maximum number of files to process
            analysis_types: Types of analysis to perform
            
        Returns:
            ProcessorResult containing the final state and JSON output
        """
        # For now, just call the standard process
        # Future enhancements can use these options
        return await self.process()


class ProcessorResult:
    """
    Container for processing results.
    
    This class wraps the final processor state and provides
    convenient access methods for the results.
    """
    
    def __init__(self, state: dict[str, Any]):
        """
        Initialize the ProcessorResult.
        
        Args:
            state: Final processor state dictionary
        """
        self._state = state

    @property
    def is_complete(self) -> bool:
        """Check if processing completed successfully."""
        return self._state.get("is_complete", False)

    @property
    def has_errors(self) -> bool:
        """Check if there were any errors during processing."""
        return len(self._state.get("errors", [])) > 0

    @property
    def errors(self) -> list[str]:
        """Get list of errors that occurred during processing."""
        return self._state.get("errors", [])

    @property
    def repository(self) -> dict[str, Any]:
        """Get repository information."""
        return self._state.get("repository", {})

    @property
    def metadata(self) -> dict[str, Any]:
        """Get extracted metadata."""
        return self._state.get("metadata", {})

    @property
    def analysis(self) -> dict[str, Any]:
        """Get analysis results."""
        return self._state.get("analysis", {})

    def to_json(self, pretty: bool = True) -> str:
        """
        Get results as JSON string.
        
        Args:
            pretty: Whether to pretty-print the JSON
            
        Returns:
            JSON string representation of results
        """
        json_output = self._state.get("json_output", "")
        
        if json_output and pretty:
            try:
                data = json.loads(json_output)
                return json.dumps(data, indent=2)
            except json.JSONDecodeError:
                return json_output
        
        return json_output

    def to_dict(self) -> dict[str, Any]:
        """
        Get results as dictionary.
        
        Returns:
            Dictionary representation of results
        """
        json_output = self._state.get("json_output", "")
        
        if json_output:
            try:
                return json.loads(json_output)
            except json.JSONDecodeError:
                pass
        
        return {
            "repository": self.repository,
            "metadata": self.metadata,
            "analysis": self.analysis
        }

    def save_to_file(self, filepath: str) -> None:
        """
        Save results to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
        """
        json_output = self.to_json(pretty=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_output)


async def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Processor Service - Extract repository metadata"
    )
    parser.add_argument(
        "--owner",
        default=os.getenv("REPOSITORY_OWNER", "Rohith-Kantipudi"),
        help="Repository owner"
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("REPOSITORY_NAME", "eShop"),
        help="Repository name"
    )
    parser.add_argument(
        "--output",
        default="output.json",
        help="Output file path"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Processing repository: {args.owner}/{args.repo}")
    
    try:
        processor = CodeProcessorService(
            repo_owner=args.owner,
            repo_name=args.repo
        )
        
        result = await processor.process()
        
        if result.has_errors:
            print("Errors occurred during processing:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.is_complete:
            result.save_to_file(args.output)
            print(f"Results saved to {args.output}")
        else:
            print("Processing did not complete successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
