"""
Tests for the JSON formatter module.
"""

import json
import pytest

from src.processors.json_formatter import JsonFormatter


class TestJsonFormatter:
    """Tests for JsonFormatter class."""
    
    @pytest.fixture
    def formatter(self):
        """Create a JsonFormatter instance."""
        return JsonFormatter()
    
    @pytest.fixture
    def sample_repository(self):
        """Create sample repository data."""
        return {
            "name": "test-repo",
            "owner": "test-owner",
            "description": "Test repository",
            "languages": ["Python", "JavaScript"],
            "default_branch": "main",
            "structure": {
                "files": [
                    {"path": "README.md", "name": "README.md"},
                    {"path": "src/main.py", "name": "main.py"}
                ],
                "directories": [
                    {"path": "src", "name": "src"}
                ],
                "total_files": 2,
                "total_directories": 1
            }
        }
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata."""
        return {
            "files": [
                {
                    "path": "src/main.py",
                    "name": "main.py",
                    "extension": ".py",
                    "size": 1024,
                    "language": "Python"
                }
            ],
            "dependencies": [
                {
                    "name": "langchain",
                    "version": "0.3.0",
                    "type": "pip",
                    "source_file": "requirements.txt"
                }
            ],
            "code_metrics": {
                "total_files": 10,
                "total_size_bytes": 50000,
                "languages_breakdown": {"Python": 8, "JavaScript": 2},
                "file_types": {".py": 8, ".js": 2}
            },
            "tech_stack": [
                {
                    "name": "Python",
                    "category": "language",
                    "version": None
                },
                {
                    "name": "LangChain",
                    "category": "framework",
                    "version": "0.3.0"
                }
            ]
        }
    
    @pytest.fixture
    def sample_analysis(self):
        """Create sample analysis."""
        return {
            "summary": "This is a test repository.",
            "insights": ["Well-structured codebase", "Good test coverage"],
            "recommendations": ["Add more documentation"]
        }

    def test_format_returns_valid_json(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test that format returns valid JSON."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed is not None
    
    def test_format_includes_all_sections(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test that format includes all required sections."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        parsed = json.loads(result)
        
        assert "repository" in parsed
        assert "metadata" in parsed
        assert "analysis" in parsed
    
    def test_format_repository_section(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test repository section formatting."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        parsed = json.loads(result)
        repo = parsed["repository"]
        
        assert repo["name"] == "test-repo"
        assert repo["owner"] == "test-owner"
        assert "Python" in repo["languages"]
        assert "structure" in repo
    
    def test_format_metadata_section(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test metadata section formatting."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        parsed = json.loads(result)
        metadata = parsed["metadata"]
        
        assert "files" in metadata
        assert "dependencies" in metadata
        assert "codeMetrics" in metadata
        assert "techStack" in metadata
    
    def test_format_analysis_section(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test analysis section formatting."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        parsed = json.loads(result)
        analysis = parsed["analysis"]
        
        assert analysis["summary"] == "This is a test repository."
        assert len(analysis["insights"]) == 2
        assert len(analysis["recommendations"]) == 1

    def test_validate_valid_json(self, formatter, sample_repository, sample_metadata, sample_analysis):
        """Test validation of valid JSON."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        assert formatter.validate(result) is True
    
    def test_validate_invalid_json(self, formatter):
        """Test validation of invalid JSON."""
        assert formatter.validate("not valid json") is False
    
    def test_validate_missing_sections(self, formatter):
        """Test validation of JSON missing required sections."""
        invalid = json.dumps({"repository": {"name": "test"}})
        assert formatter.validate(invalid) is False
    
    def test_to_dict_returns_dictionary(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test that to_dict returns a dictionary."""
        result = formatter.to_dict(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        assert isinstance(result, dict)
        assert "repository" in result
    
    def test_pretty_print_formats_json(
        self,
        formatter,
        sample_repository,
        sample_metadata,
        sample_analysis
    ):
        """Test that pretty_print formats JSON with indentation."""
        result = formatter.format(
            sample_repository,
            sample_metadata,
            sample_analysis
        )
        
        pretty = formatter.pretty_print(result)
        
        # Pretty printed JSON should have newlines
        assert "\n" in pretty
        
        # Should still be valid JSON
        json.loads(pretty)
    
    def test_format_handles_empty_data(self, formatter):
        """Test formatting with empty data."""
        result = formatter.format({}, {}, {})
        
        parsed = json.loads(result)
        assert parsed["repository"]["name"] == ""
        assert parsed["metadata"]["files"] == []
        assert parsed["analysis"]["summary"] == ""
