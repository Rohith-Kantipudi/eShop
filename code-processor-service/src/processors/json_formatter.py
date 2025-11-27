

import json
from typing import Any


class JsonFormatter:
    # Configuration constants
    MAX_FILES_IN_OUTPUT = 500
    MAX_TOP_LEVEL_ITEMS = 20
    
    def format(
        self,
        repository: dict[str, Any],
        metadata: dict[str, Any],
        analysis: dict[str, Any],
        issues: dict[str, Any] = None
    ) -> str:
        from datetime import datetime
        
        output = {
            "analysis_metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "repository": {
                    "owner": repository.get("owner", ""),
                    "name": repository.get("name", "")
                },
                "analyzer_version": "1.0.0"
            },
            "repository": self._format_repository_enhanced(repository, analysis),
            "metadata": self._format_metadata(metadata),
            "analysis": self._format_analysis(analysis)
        }
        
        if issues:
            output["issues"] = self._format_issues(issues)
        
        return json.dumps(output, indent=2, default=str)

    def _format_repository(self, repository: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": repository.get("name", ""),
            "owner": repository.get("owner", ""),
            "description": repository.get("description"),
            "languages": repository.get("languages", []),
            "defaultBranch": repository.get("default_branch", "main"),
            "structure": self._format_structure(repository.get("structure", {}))
        }
    
    def _format_repository_enhanced(self, repository: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        repo_name = repository.get("name", "")
        repo_owner = repository.get("owner", "")
        repo_description = repository.get("description", "")
        repo_stars = repository.get("stars", 0)
        
        return {
            "name": repo_name,
            "owner": repo_owner,
            "description": repo_description,
            "stars": repo_stars,
            "url": f"https://github.com/{repo_owner}/{repo_name}",
            "overview": analysis.get("summary", ""),
            "services": analysis.get("services", []),
            "connections": self._extract_connections(analysis.get("services", [])),
            "patterns": self._analyze_patterns(analysis.get("services", []))
        }

    def _format_structure(self, structure: dict[str, Any]) -> dict[str, Any]:
        return {
            "totalFiles": structure.get("total_files", 0),
            "totalDirectories": structure.get("total_directories", 0),
            "topLevelItems": self._get_top_level_items(structure)
        }

    def _get_top_level_items(self, structure: dict[str, Any]) -> list[str]:
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
        # Aggregate tech stack from services
        tech_stack = set()
        for tech in metadata.get("tech_stack", []):
            tech_stack.add(tech.get("name") if isinstance(tech, dict) else tech)
        
        return {
            "files": self._format_files(metadata.get("files", [])),
            "dependencies": self._format_dependencies(metadata.get("dependencies", [])),
            "code_metrics": self._format_code_metrics(metadata.get("code_metrics", {})),
            "tech_stack": list(tech_stack)
        }

    def _format_files(self, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
        return {
            "total_files": metrics.get("total_files", 0),
            "total_size_bytes": metrics.get("total_size_bytes", 0),
            "languages_breakdown": metrics.get("languages_breakdown", {}),
            "file_types": metrics.get("file_types", {})
        }
    
    def _extract_connections(self, services: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract service-to-service connections based on actual dependencies only."""
        connections = []
        service_names = {s.get("name") for s in services}
        
        for service in services:
            source = service.get("name")
            dependencies = service.get("dependencies", [])
            
            # Only match actual dependency references
            for dep in dependencies:
                for other_service in service_names:
                    if source != other_service:
                        # Match if service name appears in dependency
                        dep_normalized = dep.replace(".", "").replace("-", "").replace("_", "").lower()
                        service_normalized = other_service.replace(".", "").replace("-", "").replace("_", "").lower()
                        
                        if service_normalized in dep_normalized:
                            connections.append({
                                "from": source,
                                "to": other_service,
                                "type": "dependency",
                                "via": dep
                            })
        
        # Remove duplicates
        seen = set()
        unique_connections = []
        for conn in connections:
            key = (conn["from"], conn["to"], conn.get("via", ""))
            if key not in seen:
                seen.add(key)
                unique_connections.append(conn)
        
        return unique_connections
    
    def _analyze_patterns(self, services: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze architectural patterns from services - purely data-driven."""
        if not services:
            return {}
        
        # Count service types
        type_counts = {}
        for service in services:
            stype = service.get("type", "unknown")
            type_counts[stype] = type_counts.get(stype, 0) + 1
        
        # Find common technologies (used in multiple services)
        tech_count = {}
        for service in services:
            for tech in service.get("technologies", []):
                tech_count[tech] = tech_count.get(tech, 0) + 1
        
        patterns = {
            "total_services": len(services),
            "service_types": type_counts,
            "shared_technologies": {tech: count for tech, count in tech_count.items() if count > 1}
        }
        
        return patterns

    def _format_tech_stack(
        self,
        tech_stack: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return [
            {
                "name": t.get("name", ""),
                "category": t.get("category", "unknown"),
                "version": t.get("version")
            }
            for t in tech_stack
        ]

    def _format_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        return {
            "summary": analysis.get("summary", ""),
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", [])
        }
    
    def _format_issues(self, issues_data: dict[str, Any]) -> dict[str, Any]:
        issues = issues_data.get("issues", [])
        prs = issues_data.get("pull_requests", [])
        
        # Categorize issues
        categorized = {
            "bugs": [],
            "features": [],
            "enhancements": [],
            "documentation": [],
            "questions": [],
            "other": []
        }
        
        for issue in issues:
            labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
            if any("bug" in l for l in labels):
                categorized["bugs"].append(self._format_issue(issue))
            elif any("feature" in l or "enhancement" in l for l in labels):
                categorized["features"].append(self._format_issue(issue))
            elif any("doc" in l for l in labels):
                categorized["documentation"].append(self._format_issue(issue))
            elif any("question" in l for l in labels):
                categorized["questions"].append(self._format_issue(issue))
            else:
                categorized["other"].append(self._format_issue(issue))
        
        # Extract metadata
        all_labels = {}
        contributors = set()
        technologies = set()
        
        for issue in issues + prs:
            for label in issue.get("labels", []):
                label_name = label.get("name", "")
                all_labels[label_name] = all_labels.get(label_name, 0) + 1
            
            if issue.get("user"):
                contributors.add(issue["user"].get("login", ""))
            
            # Extract technologies from labels and titles
            title_lower = issue.get("title", "").lower()
            for tech in [".NET", "Blazor", "Bootstrap", "jQuery", "Duende IdentityServer", "playwright", "javascript"]:
                if tech.lower() in title_lower:
                    technologies.add(tech)
        
        return {
            "summary": {
                "total_open_issues": len([i for i in issues if i.get("state") == "open"]),
                "total_closed_issues": len([i for i in issues if i.get("state") == "closed"]),
                "total_prs": len(prs)
            },
            "categorized_issues": categorized,
            "metadata": {
                "code_owners": [],
                "active_contributors": list(contributors)[:10],
                "affected_services": [],
                "common_technologies": list(technologies),
                "issue_labels": all_labels
            },
            "patterns": {
                "common_bug_areas": [],
                "frequent_feature_requests": [],
                "pain_points": self._extract_pain_points(issues),
                "improvement_opportunities": self._extract_improvements(issues)
            },
            "recent_activity": {
                "recent_issues": [self._format_issue(i) for i in issues[:10]],
                "recent_prs": [self._format_pr(pr) for pr in prs[:10]]
            }
        }
    
    def _format_issue(self, issue: dict[str, Any]) -> dict[str, Any]:
        return {
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "state": issue.get("state", ""),
            "created_at": issue.get("created_at", ""),
            "labels": [l.get("name") for l in issue.get("labels", [])]
        }
    
    def _format_pr(self, pr: dict[str, Any]) -> dict[str, Any]:
        return {
            "number": pr.get("number"),
            "title": pr.get("title", ""),
            "created_at": pr.get("created_at", "")
        }
    
    def _extract_pain_points(self, issues: list[dict[str, Any]]) -> list[str]:
        if not issues:
            return ["No issues have been reported across all categories, indicating either low engagement or a lack of active issue tracking.",
                    "Despite a diverse set of technologies and contributors, there is minimal issue labeling and categorization."]
        return []
    
    def _extract_improvements(self, issues: list[dict[str, Any]]) -> list[str]:
        if not issues:
            return [
                "Encourage contributors to report and categorize issues to better identify areas for improvement.",
                "Increase usage of issue labels to facilitate pattern analysis and prioritization.",
                "Review and update documentation or onboarding to ensure contributors know how to submit issues."
            ]
        return []

    def to_dict(
        self,
        repository: dict[str, Any],
        metadata: dict[str, Any],
        analysis: dict[str, Any]
    ) -> dict[str, Any]:
        return json.loads(self.format(repository, metadata, analysis))

    def validate(self, json_output: str) -> bool:
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
        try:
            data = json.loads(json_output)
            return json.dumps(data, indent=2, sort_keys=False)
        except json.JSONDecodeError:
            return json_output
