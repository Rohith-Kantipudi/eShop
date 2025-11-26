"""
Tests for the processing nodes module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.graph.nodes import ProcessingNodes, should_continue
from src.graph.state import create_initial_state


class TestShouldContinue:
    """Tests for should_continue function."""
    
    def test_returns_continue_when_should_continue_is_true(self):
        """Test that 'continue' is returned when should_continue is True."""
        state = create_initial_state("owner", "repo")
        state["should_continue"] = True
        state["is_complete"] = False
        
        result = should_continue(state)
        
        assert result == "continue"
    
    def test_returns_end_when_should_continue_is_false(self):
        """Test that 'end' is returned when should_continue is False."""
        state = create_initial_state("owner", "repo")
        state["should_continue"] = False
        
        result = should_continue(state)
        
        assert result == "end"
    
    def test_returns_end_when_is_complete(self):
        """Test that 'end' is returned when is_complete is True."""
        state = create_initial_state("owner", "repo")
        state["is_complete"] = True
        
        result = should_continue(state)
        
        assert result == "end"
    
    def test_returns_continue_for_initial_state(self):
        """Test that 'continue' is returned for initial state."""
        state = create_initial_state("owner", "repo")
        
        result = should_continue(state)
        
        assert result == "continue"


class TestProcessingNodes:
    """Tests for ProcessingNodes class."""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Create a mock MCP client."""
        client = AsyncMock()
        client.get_repository_info.return_value = {
            "name": "test-repo",
            "owner": "test-owner",
            "description": "Test description",
            "languages": ["Python"],
            "default_branch": "main"
        }
        client.get_file_structure.return_value = {
            "files": [
                {"path": "README.md", "name": "README.md", "size": 100}
            ],
            "directories": [{"path": "src", "name": "src"}],
            "total_files": 1,
            "total_directories": 1
        }
        return client
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = AsyncMock()
        client.summarize_repository.return_value = {
            "summary": "Test summary",
            "insights": ["Test insight"],
            "recommendations": ["Test recommendation"]
        }
        return client
    
    @pytest.fixture
    def mock_metadata_extractor(self):
        """Create a mock metadata extractor."""
        extractor = AsyncMock()
        extractor.extract_files_metadata.return_value = [
            {"path": "README.md", "language": "Markdown"}
        ]
        extractor.extract_dependencies.return_value = []
        extractor.calculate_code_metrics.return_value = {
            "total_files": 1,
            "total_size_bytes": 100
        }
        extractor.identify_tech_stack.return_value = []
        return extractor
    
    @pytest.fixture
    def mock_code_analyzer(self):
        """Create a mock code analyzer."""
        analyzer = AsyncMock()
        analyzer.analyze.return_value = {
            "summary": "Analyzed summary",
            "insights": ["Analysis insight"],
            "recommendations": ["Analysis recommendation"]
        }
        return analyzer
    
    @pytest.fixture
    def mock_json_formatter(self):
        """Create a mock JSON formatter."""
        formatter = MagicMock()
        formatter.format.return_value = '{"test": "output"}'
        return formatter
    
    @pytest.fixture
    def nodes(
        self,
        mock_mcp_client,
        mock_llm_client,
        mock_metadata_extractor,
        mock_code_analyzer,
        mock_json_formatter
    ):
        """Create ProcessingNodes instance with mocks."""
        return ProcessingNodes(
            mcp_client=mock_mcp_client,
            llm_client=mock_llm_client,
            metadata_extractor=mock_metadata_extractor,
            code_analyzer=mock_code_analyzer,
            json_formatter=mock_json_formatter
        )

    @pytest.mark.asyncio
    async def test_analyze_repository_updates_state(self, nodes, mock_mcp_client):
        """Test that analyze_repository updates state correctly."""
        state = create_initial_state("owner", "repo")
        
        result = await nodes.analyze_repository(state)
        
        assert result["current_stage"] == "repository_analysis"
        assert result["repository"]["name"] == "test-repo"
        assert result["repository"]["owner"] == "test-owner"
        mock_mcp_client.get_repository_info.assert_called_once()
        mock_mcp_client.get_file_structure.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_repository_handles_error(self, nodes, mock_mcp_client):
        """Test that analyze_repository handles errors gracefully."""
        mock_mcp_client.get_repository_info.side_effect = Exception("API Error")
        state = create_initial_state("owner", "repo")
        
        result = await nodes.analyze_repository(state)
        
        assert len(result["errors"]) > 0
        assert result["should_continue"] is False

    @pytest.mark.asyncio
    async def test_extract_metadata_updates_state(self, nodes, mock_metadata_extractor):
        """Test that extract_metadata updates state correctly."""
        state = create_initial_state("owner", "repo")
        state["raw_files"] = [{"path": "test.py"}]
        
        result = await nodes.extract_metadata(state)
        
        assert result["current_stage"] == "metadata_extraction"
        assert "files" in result["metadata"]
        mock_metadata_extractor.extract_files_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_format_data_updates_state(self, nodes, mock_code_analyzer):
        """Test that format_data updates state correctly."""
        state = create_initial_state("owner", "repo")
        
        result = await nodes.format_data(state)
        
        assert result["current_stage"] == "data_formatting"
        assert "summary" in result["analysis"]
        mock_code_analyzer.analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_json_updates_state(self, nodes, mock_json_formatter):
        """Test that generate_json updates state correctly."""
        state = create_initial_state("owner", "repo")
        
        result = await nodes.generate_json(state)
        
        assert result["current_stage"] == "json_generation"
        assert result["json_output"] == '{"test": "output"}'
        assert result["is_complete"] is True
        mock_json_formatter.format.assert_called_once()
