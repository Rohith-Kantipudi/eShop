"""
Tests for the state module.
"""

import pytest

from src.graph.state import (
    ProcessorState,
    RepositoryInfo,
    FileMetadata,
    DependencyInfo,
    CodeMetrics,
    TechStackItem,
    AnalysisResult,
    MetadataOutput,
    create_initial_state,
)


class TestCreateInitialState:
    """Tests for create_initial_state function."""
    
    def test_creates_state_with_repo_info(self):
        """Test that initial state is created with repository info."""
        state = create_initial_state("test-owner", "test-repo")
        
        assert state["repo_owner"] == "test-owner"
        assert state["repo_name"] == "test-repo"
    
    def test_creates_state_with_default_values(self):
        """Test that initial state has correct default values."""
        state = create_initial_state("owner", "repo")
        
        assert state["current_stage"] == "init"
        assert state["raw_files"] == []
        assert state["raw_content"] == {}
        assert state["errors"] == []
        assert state["is_complete"] is False
        assert state["should_continue"] is True
    
    def test_creates_state_with_repository_info(self):
        """Test that repository info is properly initialized."""
        state = create_initial_state("owner", "repo")
        
        assert state["repository"]["name"] == "repo"
        assert state["repository"]["owner"] == "owner"
        assert state["repository"]["languages"] == []
        assert state["repository"]["structure"] == {}
    
    def test_creates_state_with_empty_metadata(self):
        """Test that metadata is properly initialized."""
        state = create_initial_state("owner", "repo")
        
        assert state["metadata"]["files"] == []
        assert state["metadata"]["dependencies"] == []
        assert state["metadata"]["code_metrics"]["total_files"] == 0
        assert state["metadata"]["tech_stack"] == []
    
    def test_creates_state_with_empty_analysis(self):
        """Test that analysis is properly initialized."""
        state = create_initial_state("owner", "repo")
        
        assert state["analysis"]["summary"] == ""
        assert state["analysis"]["insights"] == []
        assert state["analysis"]["recommendations"] == []


class TestRepositoryInfo:
    """Tests for RepositoryInfo TypedDict."""
    
    def test_repository_info_structure(self):
        """Test RepositoryInfo can be created with expected fields."""
        repo_info: RepositoryInfo = {
            "name": "test-repo",
            "owner": "test-owner",
            "description": "Test description",
            "languages": ["Python", "JavaScript"],
            "default_branch": "main",
            "structure": {"files": []}
        }
        
        assert repo_info["name"] == "test-repo"
        assert repo_info["languages"] == ["Python", "JavaScript"]


class TestFileMetadata:
    """Tests for FileMetadata TypedDict."""
    
    def test_file_metadata_structure(self):
        """Test FileMetadata can be created with expected fields."""
        file_meta: FileMetadata = {
            "path": "src/main.py",
            "name": "main.py",
            "extension": ".py",
            "size": 1024,
            "language": "Python"
        }
        
        assert file_meta["path"] == "src/main.py"
        assert file_meta["language"] == "Python"


class TestDependencyInfo:
    """Tests for DependencyInfo TypedDict."""
    
    def test_dependency_info_structure(self):
        """Test DependencyInfo can be created with expected fields."""
        dep_info: DependencyInfo = {
            "name": "langchain",
            "version": "0.3.0",
            "type": "pip",
            "source_file": "requirements.txt"
        }
        
        assert dep_info["name"] == "langchain"
        assert dep_info["type"] == "pip"


class TestCodeMetrics:
    """Tests for CodeMetrics TypedDict."""
    
    def test_code_metrics_structure(self):
        """Test CodeMetrics can be created with expected fields."""
        metrics: CodeMetrics = {
            "total_files": 100,
            "total_lines": 10000,
            "languages_breakdown": {"Python": 50, "JavaScript": 50},
            "file_types": {".py": 50, ".js": 50}
        }
        
        assert metrics["total_files"] == 100
        assert metrics["languages_breakdown"]["Python"] == 50
