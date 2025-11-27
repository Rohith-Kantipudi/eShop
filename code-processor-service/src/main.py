

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
    def __init__(
        self,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
        github_token: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None
    ):
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
        # For now, just call the standard process
        # Future enhancements can use these options
        return await self.process()


class ProcessorResult:
    def __init__(self, state: dict[str, Any]):
        self._state = state

    @property
    def is_complete(self) -> bool:
        return self._state.get("is_complete", False)

    @property
    def has_errors(self) -> bool:
        return len(self._state.get("errors", [])) > 0

    @property
    def errors(self) -> list[str]:
        return self._state.get("errors", [])

    @property
    def repository(self) -> dict[str, Any]:
        return self._state.get("repository", {})

    @property
    def metadata(self) -> dict[str, Any]:
        return self._state.get("metadata", {})

    @property
    def analysis(self) -> dict[str, Any]:
        return self._state.get("analysis", {})

    def to_json(self, pretty: bool = True) -> str:
        json_output = self._state.get("json_output", "")
        
        if json_output and pretty:
            try:
                data = json.loads(json_output)
                return json.dumps(data, indent=2)
            except json.JSONDecodeError:
                return json_output
        
        return json_output

    def to_dict(self) -> dict[str, Any]:
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
        json_output = self.to_json(pretty=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_output)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Processor Service - Extract repository metadata"
    )
    parser.add_argument(
        "--owner",
        default=os.getenv("REPOSITORY_OWNER"),
        help="Repository owner (default: from REPOSITORY_OWNER env var)"
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("REPOSITORY_NAME"),
        help="Repository name (default: from REPOSITORY_NAME env var)"
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
    
    # Validate required arguments
    if not args.owner or not args.repo:
        parser.error(
            "Repository owner and name are required. "
            "Provide --owner and --repo arguments or set "
            "REPOSITORY_OWNER and REPOSITORY_NAME environment variables."
        )
    
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
