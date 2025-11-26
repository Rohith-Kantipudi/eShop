"""
State definitions for the LangGraph workflow.

This module defines the ProcessorState TypedDict that holds all
the state information passed between processing nodes.
"""

from typing import TypedDict, Optional, Any


class RepositoryInfo(TypedDict, total=False):
    """Repository information structure."""
    name: str
    owner: str
    description: Optional[str]
    languages: list[str]
    default_branch: str
    structure: dict[str, Any]


class FileMetadata(TypedDict, total=False):
    """Individual file metadata structure."""
    path: str
    name: str
    extension: str
    size: int
    language: Optional[str]
    content_preview: Optional[str]


class DependencyInfo(TypedDict, total=False):
    """Dependency information structure."""
    name: str
    version: Optional[str]
    type: str  # e.g., "nuget", "npm", "pip"
    source_file: str


class CodeMetrics(TypedDict, total=False):
    """Code metrics structure."""
    total_files: int
    total_lines: int
    languages_breakdown: dict[str, int]
    file_types: dict[str, int]


class TechStackItem(TypedDict, total=False):
    """Technology stack item structure."""
    name: str
    category: str  # e.g., "framework", "library", "tool"
    version: Optional[str]


class AnalysisResult(TypedDict, total=False):
    """Analysis result structure."""
    summary: str
    insights: list[str]
    recommendations: list[str]


class MetadataOutput(TypedDict, total=False):
    """Complete metadata output structure."""
    files: list[FileMetadata]
    dependencies: list[DependencyInfo]
    code_metrics: CodeMetrics
    tech_stack: list[TechStackItem]


class ProcessorState(TypedDict, total=False):
    """
    Main state object for the LangGraph workflow.
    
    This TypedDict holds all the state information that is passed
    between processing nodes in the workflow.
    """
    # Input parameters
    repo_owner: str
    repo_name: str
    
    # Processing stage
    current_stage: str
    
    # Intermediate data
    raw_files: list[dict[str, Any]]
    raw_content: dict[str, str]
    
    # Repository information
    repository: RepositoryInfo
    
    # Extracted metadata
    metadata: MetadataOutput
    
    # LLM analysis results
    analysis: AnalysisResult
    
    # Final output
    json_output: str
    
    # Error handling
    errors: list[str]
    
    # Processing flags
    is_complete: bool
    should_continue: bool


def create_initial_state(repo_owner: str, repo_name: str) -> ProcessorState:
    """
    Create an initial ProcessorState with default values.
    
    Args:
        repo_owner: The GitHub repository owner
        repo_name: The GitHub repository name
        
    Returns:
        A ProcessorState with initialized default values
    """
    return ProcessorState(
        repo_owner=repo_owner,
        repo_name=repo_name,
        current_stage="init",
        raw_files=[],
        raw_content={},
        repository=RepositoryInfo(
            name=repo_name,
            owner=repo_owner,
            languages=[],
            structure={}
        ),
        metadata=MetadataOutput(
            files=[],
            dependencies=[],
            code_metrics=CodeMetrics(
                total_files=0,
                total_lines=0,
                languages_breakdown={},
                file_types={}
            ),
            tech_stack=[]
        ),
        analysis=AnalysisResult(
            summary="",
            insights=[],
            recommendations=[]
        ),
        json_output="",
        errors=[],
        is_complete=False,
        should_continue=True
    )
