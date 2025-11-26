"""
Tests for the code analyzer module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.processors.code_analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Tests for CodeAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a CodeAnalyzer instance."""
        return CodeAnalyzer()
    
    @pytest.fixture
    def sample_repository(self):
        """Create sample repository data."""
        return {
            "name": "test-repo",
            "owner": "test-owner",
            "description": "A test repository",
            "languages": ["Python", "JavaScript"],
            "readme": "# Test Repo\nThis is a test."
        }
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata."""
        return {
            "files": [
                {"path": "src/main.py", "extension": ".py", "language": "Python"},
                {"path": "tests/test_main.py", "extension": ".py", "language": "Python"},
                {"path": "README.md", "extension": ".md", "language": "Markdown"},
            ],
            "dependencies": [
                {"name": "langchain", "version": "0.3.0"},
            ],
            "code_metrics": {
                "total_files": 50,
                "languages_breakdown": {"Python": 40, "JavaScript": 10}
            },
            "tech_stack": [
                {"name": "Python", "category": "language"},
                {"name": "LangChain", "category": "framework"},
            ]
        }

    def test_generate_fallback_summary(self, analyzer, sample_repository):
        """Test fallback summary generation."""
        code_metrics = {"total_files": 100}
        
        summary = analyzer._generate_fallback_summary(
            sample_repository,
            code_metrics
        )
        
        assert "test-repo" in summary
        assert "test-owner" in summary
        assert "100 files" in summary

    def test_generate_code_insights_large_codebase(self, analyzer):
        """Test insights for large codebase."""
        code_metrics = {
            "total_files": 1500,
            "languages_breakdown": {"Python": 1000, "JavaScript": 500}
        }
        
        insights = analyzer._generate_code_insights(code_metrics, [])
        
        assert any("Large codebase" in i for i in insights)
        assert any("modularization" in i for i in insights)

    def test_generate_code_insights_medium_codebase(self, analyzer):
        """Test insights for medium codebase."""
        code_metrics = {
            "total_files": 200,
            "languages_breakdown": {"Python": 200}
        }
        
        insights = analyzer._generate_code_insights(code_metrics, [])
        
        assert any("Medium-sized" in i for i in insights)

    def test_generate_code_insights_multi_language(self, analyzer):
        """Test insights for multi-language project."""
        code_metrics = {
            "total_files": 100,
            "languages_breakdown": {
                "Python": 30, "JavaScript": 20, "TypeScript": 15,
                "Go": 15, "Ruby": 10, "Rust": 10
            }
        }
        
        insights = analyzer._generate_code_insights(code_metrics, [])
        
        assert any("Multi-language" in i for i in insights)
        assert any("6 languages" in i for i in insights)

    def test_generate_code_insights_primary_language(self, analyzer):
        """Test primary language identification."""
        code_metrics = {
            "total_files": 100,
            "languages_breakdown": {"Python": 80, "JavaScript": 20}
        }
        
        insights = analyzer._generate_code_insights(code_metrics, [])
        
        assert any("Python" in i and "80 files" in i for i in insights)

    def test_generate_code_insights_frameworks(self, analyzer):
        """Test framework detection in insights."""
        code_metrics = {"total_files": 50, "languages_breakdown": {}}
        tech_stack = [
            {"name": "React", "category": "framework"},
            {"name": "Express.js", "category": "framework"},
        ]
        
        insights = analyzer._generate_code_insights(code_metrics, tech_stack)
        
        assert any("React" in i or "Express" in i for i in insights)

    def test_generate_recommendations_no_docs(self, analyzer):
        """Test recommendation for missing documentation."""
        metadata = {
            "files": [
                {"path": "src/main.py", "extension": ".py"},
                {"path": "README.md", "extension": ".md"},
            ],
            "dependencies": []
        }
        
        recommendations = analyzer._generate_recommendations(metadata)
        
        assert any("documentation" in r.lower() for r in recommendations)

    def test_generate_recommendations_no_tests(self, analyzer):
        """Test recommendation for missing tests."""
        metadata = {
            "files": [
                {"path": "src/main.py", "extension": ".py"},
            ],
            "dependencies": []
        }
        
        recommendations = analyzer._generate_recommendations(metadata)
        
        assert any("test" in r.lower() for r in recommendations)

    def test_generate_recommendations_has_tests(self, analyzer):
        """Test no test recommendation when tests exist."""
        metadata = {
            "files": [
                {"path": "src/main.py", "extension": ".py"},
                {"path": "tests/test_main.py", "extension": ".py"},
            ],
            "dependencies": []
        }
        
        recommendations = analyzer._generate_recommendations(metadata)
        
        assert not any("No test files detected" in r for r in recommendations)

    def test_generate_recommendations_no_ci(self, analyzer):
        """Test recommendation for missing CI/CD."""
        metadata = {
            "files": [
                {"path": "src/main.py", "extension": ".py"},
            ],
            "dependencies": []
        }
        
        recommendations = analyzer._generate_recommendations(metadata)
        
        assert any("CI/CD" in r for r in recommendations)

    def test_generate_recommendations_has_ci(self, analyzer):
        """Test no CI recommendation when CI exists."""
        metadata = {
            "files": [
                {"path": ".github/workflows/ci.yml"},
            ],
            "dependencies": []
        }
        
        recommendations = analyzer._generate_recommendations(metadata)
        
        assert not any("setting up CI/CD" in r for r in recommendations)

    @pytest.mark.asyncio
    async def test_analyze_returns_analysis_result(
        self,
        analyzer,
        sample_repository,
        sample_metadata
    ):
        """Test that analyze returns expected structure."""
        # Mock LLM client
        mock_llm = AsyncMock()
        mock_llm.summarize_repository.return_value = {
            "summary": "Test summary",
            "insights": ["LLM insight 1"],
            "recommendations": ["LLM recommendation 1"]
        }
        
        result = await analyzer.analyze(
            sample_repository,
            sample_metadata,
            mock_llm
        )
        
        assert "summary" in result
        assert "insights" in result
        assert "recommendations" in result
        assert isinstance(result["insights"], list)
        assert isinstance(result["recommendations"], list)
