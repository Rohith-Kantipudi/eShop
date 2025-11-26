"""
LangGraph workflow definition for code processing.

This module defines the main workflow graph that orchestrates
the code processing pipeline using LangGraph.
"""

from typing import Optional

from langgraph.graph import StateGraph, END

from .state import ProcessorState, create_initial_state
from .nodes import ProcessingNodes, should_continue
from ..mcp import GitHubMCPClient
from ..llm import AzureOpenAIClient
from ..processors import MetadataExtractor, CodeAnalyzer, JsonFormatter


class CodeProcessorWorkflow:
    """
    LangGraph-based workflow for processing repository code metadata.
    
    This class creates and manages a StateGraph that orchestrates
    the code processing pipeline with conditional routing.
    """
    
    def __init__(
        self,
        mcp_client: GitHubMCPClient,
        llm_client: AzureOpenAIClient,
        metadata_extractor: Optional[MetadataExtractor] = None,
        code_analyzer: Optional[CodeAnalyzer] = None,
        json_formatter: Optional[JsonFormatter] = None
    ):
        """
        Initialize the workflow with required dependencies.
        
        Args:
            mcp_client: GitHub MCP client for repository access
            llm_client: Azure OpenAI client for LLM operations
            metadata_extractor: Optional custom metadata extractor
            code_analyzer: Optional custom code analyzer
            json_formatter: Optional custom JSON formatter
        """
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.metadata_extractor = metadata_extractor or MetadataExtractor()
        self.code_analyzer = code_analyzer or CodeAnalyzer()
        self.json_formatter = json_formatter or JsonFormatter()
        
        # Initialize processing nodes
        self.nodes = ProcessingNodes(
            mcp_client=self.mcp_client,
            llm_client=self.llm_client,
            metadata_extractor=self.metadata_extractor,
            code_analyzer=self.code_analyzer,
            json_formatter=self.json_formatter
        )
        
        # Build the workflow graph
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph for code processing.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Create a new StateGraph with ProcessorState
        workflow = StateGraph(ProcessorState)
        
        # Add processing nodes
        workflow.add_node("analyze_repository", self.nodes.analyze_repository)
        workflow.add_node("extract_metadata", self.nodes.extract_metadata)
        workflow.add_node("format_data", self.nodes.format_data)
        workflow.add_node("generate_json", self.nodes.generate_json)
        
        # Set the entry point
        workflow.set_entry_point("analyze_repository")
        
        # Add conditional edges for workflow control
        workflow.add_conditional_edges(
            "analyze_repository",
            should_continue,
            {
                "continue": "extract_metadata",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "extract_metadata",
            should_continue,
            {
                "continue": "format_data",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "format_data",
            should_continue,
            {
                "continue": "generate_json",
                "end": END
            }
        )
        
        # Final node goes to END
        workflow.add_edge("generate_json", END)
        
        # Compile the graph
        return workflow.compile()

    async def process(self, repo_owner: str, repo_name: str) -> ProcessorState:
        """
        Execute the workflow to process a repository.
        
        Args:
            repo_owner: The GitHub repository owner
            repo_name: The GitHub repository name
            
        Returns:
            Final ProcessorState with all extracted metadata and analysis
        """
        # Create initial state
        initial_state = create_initial_state(repo_owner, repo_name)
        
        # Execute the workflow
        final_state = await self._graph.ainvoke(initial_state)
        
        return final_state

    def get_graph(self) -> StateGraph:
        """
        Get the compiled workflow graph.
        
        Returns:
            The compiled StateGraph
        """
        return self._graph
