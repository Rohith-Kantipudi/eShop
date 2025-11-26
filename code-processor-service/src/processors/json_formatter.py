"""
JSON formatter for structured output.

This module provides functionality to format extracted metadata
and analysis results into the specified JSON schema.
"""

import json
from typing import Any


class JsonFormatter:
    """
    Formats extracted data into structured JSON output.
    
    This class combines repository information, metadata, and
    analysis results into the final JSON output format.
    """
    
    # Configuration constants
    MAX_FILES_IN_OUTPUT = 500
    MAX_TOP_LEVEL_ITEMS = 20
    
    def format(
        self,
        repository: dict[str, Any],
        metadata: dict[str, Any],
        analysis: dict[str, Any]
    ) -> str:
        """
        Format data into the specified JSON schema.
        
        Args:
            repository: Repository information dictionary
            metadata: Extracted metadata dictionary
            analysis: Analysis results dictionary
            
        Returns:
            Formatted JSON string
        """
        output = {
            "repository": self._format_repository(repository),
            "metadata": self._format_metadata(metadata),
            "analysis": self._format_analysis(analysis)
        }
        
        return json.dumps(output, indent=2, default=str)

    def _format_repository(self, repository: dict[str, Any]) -> dict[str, Any]:
        """Format repository information section."""
        return {
            "name": repository.get("name", ""),
            "owner": repository.get("owner", ""),
            "description": repository.get("description"),
            "languages": repository.get("languages", []),
            "defaultBranch": repository.get("default_branch", "main"),
            "structure": self._format_structure(repository.get("structure", {}))
        }

    def _format_structure(self, structure: dict[str, Any]) -> dict[str, Any]:
        """Format repository structure information."""
        return {
            "totalFiles": structure.get("total_files", 0),
            "totalDirectories": structure.get("total_directories", 0),
            "topLevelItems": self._get_top_level_items(structure)
        }

    def _get_top_level_items(self, structure: dict[str, Any]) -> list[str]:
        """Get top-level directory and file names."""
        items = []
        
        for file in structure.get("files", [])[:self.MAX_TOP_LEVEL_ITEMS]:
            path = file.get("path", "")
            if "/" not in path:
                items.append(path)
        
        for directory in structure.get("directories", [])[:self.MAX_TOP_LEVEL_ITEMS]:
            path = directory.get("path", "")
            if "/" not in path:
                items.append(path + "/")
        
        return items

    def _format_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Format metadata section."""
        return {
            "files": self._format_files(metadata.get("files", [])),
            "dependencies": self._format_dependencies(metadata.get("dependencies", [])),
            "codeMetrics": self._format_code_metrics(metadata.get("code_metrics", {})),
            "techStack": self._format_tech_stack(metadata.get("tech_stack", []))
        }

    def _format_files(self, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Format files information."""
        return [
            {
                "path": f.get("path", ""),
                "name": f.get("name", ""),
                "extension": f.get("extension", ""),
                "size": f.get("size", 0),
                "language": f.get("language")
            }
            for f in files[:self.MAX_FILES_IN_OUTPUT]
        ]

    def _format_dependencies(
        self,
        dependencies: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Format dependencies information."""
        return [
            {
                "name": d.get("name", ""),
                "version": d.get("version"),
                "type": d.get("type", "unknown"),
                "sourceFile": d.get("source_file", "")
            }
            for d in dependencies
        ]

    def _format_code_metrics(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Format code metrics information."""
        return {
            "totalFiles": metrics.get("total_files", 0),
            "totalSizeBytes": metrics.get("total_size_bytes", 0),
            "languagesBreakdown": metrics.get("languages_breakdown", {}),
            "fileTypes": metrics.get("file_types", {})
        }

    def _format_tech_stack(
        self,
        tech_stack: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Format technology stack information."""
        return [
            {
                "name": t.get("name", ""),
                "category": t.get("category", "unknown"),
                "version": t.get("version")
            }
            for t in tech_stack
        ]

    def _format_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Format analysis section."""
        return {
            "summary": analysis.get("summary", ""),
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", [])
        }

    def to_dict(
        self,
        repository: dict[str, Any],
        metadata: dict[str, Any],
        analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Get formatted data as a dictionary.
        
        Args:
            repository: Repository information dictionary
            metadata: Extracted metadata dictionary
            analysis: Analysis results dictionary
            
        Returns:
            Formatted dictionary
        """
        return json.loads(self.format(repository, metadata, analysis))

    def validate(self, json_output: str) -> bool:
        """
        Validate JSON output against schema.
        
        Args:
            json_output: JSON string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            data = json.loads(json_output)
            
            # Check required top-level keys
            required_keys = ["repository", "metadata", "analysis"]
            if not all(key in data for key in required_keys):
                return False
            
            # Check repository structure
            repo = data["repository"]
            if "name" not in repo or "owner" not in repo:
                return False
            
            # Check metadata structure
            metadata = data["metadata"]
            metadata_keys = ["files", "dependencies", "codeMetrics", "techStack"]
            if not all(key in metadata for key in metadata_keys):
                return False
            
            # Check analysis structure
            analysis = data["analysis"]
            analysis_keys = ["summary", "insights", "recommendations"]
            if not all(key in analysis for key in analysis_keys):
                return False
            
            return True
            
        except json.JSONDecodeError:
            return False

    def pretty_print(self, json_output: str) -> str:
        """
        Pretty print JSON output.
        
        Args:
            json_output: JSON string to format
            
        Returns:
            Pretty-printed JSON string
        """
        try:
            data = json.loads(json_output)
            return json.dumps(data, indent=2, sort_keys=False)
        except json.JSONDecodeError:
            return json_output
