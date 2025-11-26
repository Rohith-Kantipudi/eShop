"""
Processing nodes for the LangGraph workflow.

This module defines the individual processing nodes that perform
specific tasks in the code processing pipeline.
"""

from typing import TYPE_CHECKING

from .state import ProcessorState

if TYPE_CHECKING:
    from ..mcp import GitHubMCPClient
    from ..llm import AzureOpenAIClient
    from ..processors import MetadataExtractor, CodeAnalyzer, JsonFormatter


class ProcessingNodes:
    """
    Collection of processing nodes for the LangGraph workflow.
    
    Each method represents a node in the workflow graph and takes
    the current state as input, returning an updated state.
    """
    
    def __init__(
        self,
        mcp_client: "GitHubMCPClient",
        llm_client: "AzureOpenAIClient",
        metadata_extractor: "MetadataExtractor",
        code_analyzer: "CodeAnalyzer",
        json_formatter: "JsonFormatter"
    ):
        """
        Initialize the processing nodes with required dependencies.
        
        Args:
            mcp_client: GitHub MCP client for repository access
            llm_client: Azure OpenAI client for LLM operations
            metadata_extractor: Metadata extraction processor
            code_analyzer: Code analysis processor
            json_formatter: JSON formatting processor
        """
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.metadata_extractor = metadata_extractor
        self.code_analyzer = code_analyzer
        self.json_formatter = json_formatter

    async def analyze_repository(self, state: ProcessorState) -> ProcessorState:
        """
        Node: Analyze repository structure and basic information.
        
        This node fetches repository metadata, file structure, and
        language information from GitHub.
        
        Args:
            state: Current processor state
            
        Returns:
            Updated state with repository information
        """
        try:
            state["current_stage"] = "repository_analysis"
            
            # Get repository information via MCP
            repo_info = await self.mcp_client.get_repository_info(
                state["repo_owner"],
                state["repo_name"]
            )
            
            # Get file structure
            file_structure = await self.mcp_client.get_file_structure(
                state["repo_owner"],
                state["repo_name"]
            )
            
            # Update state with repository information
            state["repository"] = {
                "name": repo_info.get("name", state["repo_name"]),
                "owner": repo_info.get("owner", state["repo_owner"]),
                "description": repo_info.get("description"),
                "languages": repo_info.get("languages", []),
                "default_branch": repo_info.get("default_branch", "main"),
                "structure": file_structure
            }
            
            state["raw_files"] = file_structure.get("files", [])
            
        except Exception as e:
            state["errors"].append(f"Repository analysis failed: {str(e)}")
            state["should_continue"] = False
            
        return state

    async def extract_metadata(self, state: ProcessorState) -> ProcessorState:
        """
        Node: Extract metadata from repository files.
        
        This node processes files to extract dependencies, code metrics,
        and technology stack information.
        
        Args:
            state: Current processor state
            
        Returns:
            Updated state with extracted metadata
        """
        try:
            state["current_stage"] = "metadata_extraction"
            
            # Extract file metadata
            files_metadata = await self.metadata_extractor.extract_files_metadata(
                state["raw_files"],
                self.mcp_client,
                state["repo_owner"],
                state["repo_name"]
            )
            
            # Extract dependencies
            dependencies = await self.metadata_extractor.extract_dependencies(
                state["raw_files"],
                self.mcp_client,
                state["repo_owner"],
                state["repo_name"]
            )
            
            # Calculate code metrics
            code_metrics = self.metadata_extractor.calculate_code_metrics(
                files_metadata
            )
            
            # Identify technology stack
            tech_stack = self.metadata_extractor.identify_tech_stack(
                files_metadata,
                dependencies
            )
            
            # Update state with metadata
            state["metadata"] = {
                "files": files_metadata,
                "dependencies": dependencies,
                "code_metrics": code_metrics,
                "tech_stack": tech_stack
            }
            
        except Exception as e:
            state["errors"].append(f"Metadata extraction failed: {str(e)}")
            state["should_continue"] = False
            
        return state

    async def format_data(self, state: ProcessorState) -> ProcessorState:
        """
        Node: Format extracted data for analysis.
        
        This node prepares the data for LLM analysis by organizing
        and summarizing the extracted information.
        
        Args:
            state: Current processor state
            
        Returns:
            Updated state with formatted data
        """
        try:
            state["current_stage"] = "data_formatting"
            
            # Analyze code with LLM assistance
            analysis = await self.code_analyzer.analyze(
                state["repository"],
                state["metadata"],
                self.llm_client
            )
            
            state["analysis"] = analysis
            
        except Exception as e:
            state["errors"].append(f"Data formatting failed: {str(e)}")
            state["should_continue"] = False
            
        return state

    async def generate_json(self, state: ProcessorState) -> ProcessorState:
        """
        Node: Generate final JSON output.
        
        This node combines all extracted metadata and analysis into
        the final JSON output format.
        
        Args:
            state: Current processor state
            
        Returns:
            Updated state with JSON output
        """
        try:
            state["current_stage"] = "json_generation"
            
            # Format to JSON
            json_output = self.json_formatter.format(
                repository=state["repository"],
                metadata=state["metadata"],
                analysis=state["analysis"]
            )
            
            state["json_output"] = json_output
            state["is_complete"] = True
            
        except Exception as e:
            state["errors"].append(f"JSON generation failed: {str(e)}")
            state["should_continue"] = False
            
        return state


def should_continue(state: ProcessorState) -> str:
    """
    Conditional edge function to determine workflow continuation.
    
    Args:
        state: Current processor state
        
    Returns:
        "continue" if processing should continue, "end" otherwise
    """
    if not state.get("should_continue", True):
        return "end"
    if state.get("is_complete", False):
        return "end"
    return "continue"
