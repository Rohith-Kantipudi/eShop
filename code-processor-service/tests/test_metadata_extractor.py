"""
Tests for the metadata extractor module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.processors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    """Tests for MetadataExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create a MetadataExtractor instance."""
        return MetadataExtractor()
    
    @pytest.fixture
    def sample_files(self):
        """Create sample file list."""
        return [
            {"path": "src/main.py", "name": "main.py", "size": 1024},
            {"path": "src/utils.py", "name": "utils.py", "size": 512},
            {"path": "package.json", "name": "package.json", "size": 256},
            {"path": "README.md", "name": "README.md", "size": 2048},
            {"path": "Dockerfile", "name": "Dockerfile", "size": 128},
            {"path": "src/app.ts", "name": "app.ts", "size": 1536},
        ]

    @pytest.mark.asyncio
    async def test_extract_files_metadata_detects_languages(
        self,
        extractor,
        sample_files
    ):
        """Test that file metadata extraction detects languages."""
        mock_client = MagicMock()
        
        result = await extractor.extract_files_metadata(
            sample_files,
            mock_client,
            "owner",
            "repo"
        )
        
        # Check Python files detected
        python_files = [f for f in result if f.get("language") == "Python"]
        assert len(python_files) == 2
        
        # Check TypeScript file detected
        ts_files = [f for f in result if f.get("language") == "TypeScript"]
        assert len(ts_files) == 1
        
        # Check Markdown detected
        md_files = [f for f in result if f.get("language") == "Markdown"]
        assert len(md_files) == 1
    
    @pytest.mark.asyncio
    async def test_extract_files_metadata_handles_dockerfile(
        self,
        extractor,
        sample_files
    ):
        """Test that Dockerfile is detected as Docker language."""
        mock_client = MagicMock()
        
        result = await extractor.extract_files_metadata(
            sample_files,
            mock_client,
            "owner",
            "repo"
        )
        
        docker_files = [f for f in result if f.get("language") == "Docker"]
        assert len(docker_files) == 1

    def test_calculate_code_metrics(self, extractor):
        """Test code metrics calculation."""
        files_metadata = [
            {"path": "a.py", "extension": ".py", "size": 100, "language": "Python"},
            {"path": "b.py", "extension": ".py", "size": 200, "language": "Python"},
            {"path": "c.js", "extension": ".js", "size": 150, "language": "JavaScript"},
        ]
        
        metrics = extractor.calculate_code_metrics(files_metadata)
        
        assert metrics["total_files"] == 3
        assert metrics["total_size_bytes"] == 450
        assert metrics["languages_breakdown"]["Python"] == 2
        assert metrics["languages_breakdown"]["JavaScript"] == 1
        assert metrics["file_types"][".py"] == 2
        assert metrics["file_types"][".js"] == 1

    def test_identify_tech_stack_from_languages(self, extractor):
        """Test tech stack identification from languages."""
        files_metadata = [
            {"path": "a.py", "language": "Python"},
            {"path": "b.cs", "language": "C#"},
        ]
        
        tech_stack = extractor.identify_tech_stack(files_metadata, [])
        
        language_names = [t["name"] for t in tech_stack if t["category"] == "language"]
        assert "Python" in language_names
        assert "C#" in language_names

    def test_identify_tech_stack_from_dependencies(self, extractor):
        """Test tech stack identification from dependencies."""
        files_metadata = []
        dependencies = [
            {"name": "react", "version": "18.0.0"},
            {"name": "express", "version": "4.18.0"},
            {"name": "Microsoft.AspNetCore.Mvc", "version": "6.0.0"},
        ]
        
        tech_stack = extractor.identify_tech_stack(files_metadata, dependencies)
        
        names = [t["name"] for t in tech_stack]
        assert "React" in names
        assert "Express.js" in names
        assert "ASP.NET Core" in names

    def test_identify_tech_stack_detects_docker(self, extractor):
        """Test that Docker is detected from Dockerfile."""
        files_metadata = [
            {"path": "Dockerfile", "name": "dockerfile", "language": "Docker"},
        ]
        
        tech_stack = extractor.identify_tech_stack(files_metadata, [])
        
        names = [t["name"] for t in tech_stack]
        assert "Docker" in names

    def test_identify_tech_stack_detects_github_actions(self, extractor):
        """Test that GitHub Actions is detected from workflow files."""
        files_metadata = [
            {"path": ".github/workflows/ci.yml", "name": "ci.yml"},
        ]
        
        tech_stack = extractor.identify_tech_stack(files_metadata, [])
        
        names = [t["name"] for t in tech_stack]
        assert "GitHub Actions" in names

    def test_parse_npm_dependencies(self, extractor):
        """Test parsing npm package.json dependencies."""
        content = '''{
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }'''
        
        deps = extractor._parse_npm_dependencies(content, "package.json")
        
        assert len(deps) == 3
        dep_names = [d["name"] for d in deps]
        assert "express" in dep_names
        assert "lodash" in dep_names
        assert "jest" in dep_names

    def test_parse_pip_dependencies(self, extractor):
        """Test parsing pip requirements.txt dependencies."""
        content = '''langchain>=0.3.0
aiohttp==3.9.0
# This is a comment
pydantic>=2.0.0
'''
        
        deps = extractor._parse_pip_dependencies(content, "requirements.txt")
        
        assert len(deps) == 3
        dep_names = [d["name"] for d in deps]
        assert "langchain" in dep_names
        assert "aiohttp" in dep_names
        assert "pydantic" in dep_names

    def test_parse_nuget_dependencies(self, extractor):
        """Test parsing NuGet .csproj dependencies."""
        content = '''<Project>
    <ItemGroup>
        <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
        <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    </ItemGroup>
</Project>'''
        
        deps = extractor._parse_nuget_dependencies(content, "test.csproj")
        
        assert len(deps) == 2
        dep_names = [d["name"] for d in deps]
        assert "Microsoft.Extensions.Logging" in dep_names
        assert "Newtonsoft.Json" in dep_names

    def test_parse_go_dependencies(self, extractor):
        """Test parsing Go mod dependencies."""
        content = '''module example.com/test

go 1.21

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.0
)
'''
        
        deps = extractor._parse_go_dependencies(content, "go.mod")
        
        assert len(deps) == 2
        dep_names = [d["name"] for d in deps]
        assert "github.com/gin-gonic/gin" in dep_names

    def test_get_dependency_type_npm(self, extractor):
        """Test dependency type detection for npm."""
        assert extractor._get_dependency_type("package.json") == "npm"

    def test_get_dependency_type_pip(self, extractor):
        """Test dependency type detection for pip."""
        assert extractor._get_dependency_type("requirements.txt") == "pip"

    def test_get_dependency_type_nuget(self, extractor):
        """Test dependency type detection for NuGet."""
        assert extractor._get_dependency_type("test.csproj") == "nuget"
        assert extractor._get_dependency_type("Directory.Packages.props") == "nuget"

    def test_get_dependency_type_unknown(self, extractor):
        """Test dependency type detection for unknown files."""
        assert extractor._get_dependency_type("random.txt") is None
