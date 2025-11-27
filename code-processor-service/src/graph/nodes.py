

from typing import TYPE_CHECKING

from .state import ProcessorState

if TYPE_CHECKING:
    from ..mcp import GitHubMCPClient
    from ..llm import AzureOpenAIClient
    from ..processors import MetadataExtractor, CodeAnalyzer, JsonFormatter


class ProcessingNodes:
    def __init__(
        self,
        mcp_client: "GitHubMCPClient",
        llm_client: "AzureOpenAIClient",
        metadata_extractor: "MetadataExtractor",
        code_analyzer: "CodeAnalyzer",
        json_formatter: "JsonFormatter"
    ):
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.metadata_extractor = metadata_extractor
        self.code_analyzer = code_analyzer
        self.json_formatter = json_formatter

    async def analyze_repository(self, state: ProcessorState) -> ProcessorState:
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
            
            # Get GitHub issues and PRs
            try:
                issues_data = await self.mcp_client.get_issues(
                    state["repo_owner"],
                    state["repo_name"]
                )
                state["issues"] = issues_data
            except Exception as e:
                print(f"Warning: Could not fetch issues: {e}")
                state["issues"] = {"issues": [], "pull_requests": []}
            
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
            
            # Extract services structure with dependencies
            services = self.metadata_extractor.extract_services(
                state["raw_files"],
                dependencies
            )
            
            # Update state with metadata
            state["metadata"] = {
                "files": files_metadata,
                "dependencies": dependencies,
                "code_metrics": code_metrics,
                "tech_stack": tech_stack,
                "services": services
            }
            
        except Exception as e:
            state["errors"].append(f"Metadata extraction failed: {str(e)}")
            state["should_continue"] = False
            
        return state

    async def format_data(self, state: ProcessorState) -> ProcessorState:
        try:
            state["current_stage"] = "data_formatting"
            
            # Enterprise analysis: Pass MCP client to fetch actual code
            analysis = await self.code_analyzer.analyze(
                state["repository"],
                state["metadata"],
                self.llm_client,
                state.get("issues", {"issues": [], "pull_requests": []}),
                self.mcp_client  # Pass MCP to fetch actual files
            )
            
            state["analysis"] = analysis
            
        except Exception as e:
            state["errors"].append(f"Data formatting failed: {str(e)}")
            state["should_continue"] = False
            
        return state

    async def generate_json(self, state: ProcessorState) -> ProcessorState:
        try:
            state["current_stage"] = "json_generation"
            
            # Format to JSON
            json_output = self.json_formatter.format(
                repository=state["repository"],
                metadata=state["metadata"],
                analysis=state["analysis"],
                issues=state.get("issues")
            )
            
            state["json_output"] = json_output
            state["is_complete"] = True
            
        except Exception as e:
            state["errors"].append(f"JSON generation failed: {str(e)}")
            state["should_continue"] = False
            
        return state


def should_continue(state: ProcessorState) -> str:
    if not state.get("should_continue", True):
        return "end"
    if state.get("is_complete", False):
        return "end"
    return "continue"
