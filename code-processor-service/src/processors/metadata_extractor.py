

import os
import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mcp import GitHubMCPClient


class MetadataExtractor:
    # File extension to language mapping
    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript",
        ".tsx": "TypeScript",
        ".cs": "C#",
        ".java": "Java",
        ".go": "Go",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".cpp": "C++",
        ".c": "C",
        ".h": "C/C++",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".r": "R",
        ".sql": "SQL",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sass": "SASS",
        ".less": "LESS",
        ".json": "JSON",
        ".xml": "XML",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".md": "Markdown",
        ".txt": "Text",
        ".sh": "Shell",
        ".bash": "Bash",
        ".ps1": "PowerShell",
        ".dockerfile": "Docker",
        ".tf": "Terraform",
    }
    
    # Dependency file patterns
    DEPENDENCY_PATTERNS = {
        "package.json": "npm",
        "requirements.txt": "pip",
        "Pipfile": "pipenv",
        "pyproject.toml": "poetry",
        "Gemfile": "bundler",
        "go.mod": "go",
        "Cargo.toml": "cargo",
        "pom.xml": "maven",
        "build.gradle": "gradle",
        "*.csproj": "nuget",
        "Directory.Packages.props": "nuget",
        "packages.config": "nuget",
    }

    def extract_services(self, files: list[dict[str, Any]], dependencies: list[dict[str, Any]] = None) -> list[dict[str, Any]]:
        services = {}
        dependencies = dependencies or []
        
        for file in files:
            path = file.get("path", "")
            parts = path.split("/")
            
            # Look for service indicators in src/ directory
            if len(parts) >= 2 and parts[0] == "src":
                service_name = parts[1]
                if service_name not in services:
                    services[service_name] = {
                        "name": service_name,
                        "technologies": set(),
                        "dependencies": [],
                        "type": "library",
                        "port": None,
                        "files": []
                    }
                
                services[service_name]["files"].append(file)
        
        # Analyze each service
        result = []
        for service_name, service_data in services.items():
            service_files = service_data["files"]
            
            # Basic service detection - let LLM handle detailed analysis
            service_type = "service"
            
            # Just collect file extensions and names - LLM will analyze the actual content
            file_extensions = set()
            key_files = []
            
            for file in service_files:
                filename = file.get("name", "")
                ext = os.path.splitext(filename)[1]
                if ext:
                    file_extensions.add(ext)
                
                # Track important filenames for LLM analysis
                key_files.append(filename)
            
            # Get dependencies for this service
            service_deps = [d for d in dependencies if d.get("source_file", "").startswith(f"src/{service_name}")]
            
            result.append({
                "name": service_name,
                "file_extensions": sorted(list(file_extensions)),
                "key_files": key_files[:20],  # Limit to top 20 files
                "dependencies": [d.get("name") for d in service_deps[:15]],
                "type": service_type,
                "file_count": len(service_files)
            })
        
        return result
    
    async def extract_files_metadata(
        self,
        files: list[dict[str, Any]],
        mcp_client: "GitHubMCPClient",
        owner: str,
        repo: str
    ) -> list[dict[str, Any]]:
        file_metadata = []
        
        for file_info in files:
            path = file_info.get("path", "")
            name = file_info.get("name", "")
            size = file_info.get("size", 0)
            
            # Get file extension
            _, ext = os.path.splitext(name.lower())
            
            # Determine language
            language = self.LANGUAGE_MAP.get(ext)
            
            # Handle special filenames
            if name.lower() == "dockerfile":
                language = "Docker"
            elif name.lower() in ["makefile", "gnumakefile"]:
                language = "Make"
            
            metadata = {
                "path": path,
                "name": name,
                "extension": ext,
                "size": size,
                "language": language
            }
            
            file_metadata.append(metadata)
        
        return file_metadata

    async def extract_dependencies(
        self,
        files: list[dict[str, Any]],
        mcp_client: "GitHubMCPClient",
        owner: str,
        repo: str
    ) -> list[dict[str, Any]]:
        dependencies = []
        
        for file_info in files:
            name = file_info.get("name", "")
            path = file_info.get("path", "")
            
            # Check if this is a dependency file
            dep_type = self._get_dependency_type(name)
            
            if dep_type:
                try:
                    content = await mcp_client.get_file_content(owner, repo, path)
                    deps = self._parse_dependencies(content, dep_type, path)
                    dependencies.extend(deps)
                except Exception:
                    # Skip files that can't be read
                    pass
        
        return dependencies

    def _get_dependency_type(self, filename: str) -> str | None:
        for pattern, dep_type in self.DEPENDENCY_PATTERNS.items():
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return dep_type
            elif filename == pattern:
                return dep_type
        return None

    def _parse_dependencies(
        self,
        content: str,
        dep_type: str,
        source_file: str
    ) -> list[dict[str, Any]]:
        dependencies = []
        
        if dep_type == "npm":
            dependencies = self._parse_npm_dependencies(content, source_file)
        elif dep_type == "pip":
            dependencies = self._parse_pip_dependencies(content, source_file)
        elif dep_type == "nuget":
            dependencies = self._parse_nuget_dependencies(content, source_file)
        elif dep_type == "go":
            dependencies = self._parse_go_dependencies(content, source_file)
        
        return dependencies

    def _parse_npm_dependencies(
        self,
        content: str,
        source_file: str
    ) -> list[dict[str, Any]]:
        import json
        
        dependencies = []
        
        try:
            data = json.loads(content)
            
            for dep_key in ["dependencies", "devDependencies", "peerDependencies"]:
                for name, version in data.get(dep_key, {}).items():
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": dep_key,
                        "source_file": source_file
                    })
        except json.JSONDecodeError:
            pass
        
        return dependencies

    def _parse_pip_dependencies(
        self,
        content: str,
        source_file: str
    ) -> list[dict[str, Any]]:
        dependencies = []
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse requirement line (limit line length to prevent ReDoS)
            if len(line) > 500:
                continue
            # Use non-greedy matching and atomic pattern for version
            match = re.match(r"^([a-zA-Z0-9][a-zA-Z0-9_-]{0,100})(?:\s*([<>=!~]{1,3})\s*([^\s#]{1,100}))?", line)
            if match:
                name = match.group(1)
                version = match.group(3) if match.group(2) else None
                
                dependencies.append({
                    "name": name,
                    "version": version,
                    "type": "pip",
                    "source_file": source_file
                })
        
        return dependencies

    def _parse_nuget_dependencies(
        self,
        content: str,
        source_file: str
    ) -> list[dict[str, Any]]:
        dependencies = []
        
        # Parse PackageReference elements
        pattern = r'<PackageReference\s+Include="([^"]+)"(?:\s+Version="([^"]+)")?'
        
        for match in re.finditer(pattern, content):
            name = match.group(1)
            version = match.group(2)
            
            dependencies.append({
                "name": name,
                "version": version,
                "type": "nuget",
                "source_file": source_file
            })
        
        return dependencies

    def _parse_go_dependencies(
        self,
        content: str,
        source_file: str
    ) -> list[dict[str, Any]]:
        dependencies = []
        
        # Parse require statements
        in_require_block = False
        
        for line in content.split("\n"):
            line = line.strip()
            
            if line == "require (":
                in_require_block = True
                continue
            elif line == ")":
                in_require_block = False
                continue
            
            if in_require_block or line.startswith("require "):
                # Parse module path and version
                match = re.match(r"(?:require\s+)?([^\s]+)\s+(.+)$", line)
                if match:
                    dependencies.append({
                        "name": match.group(1),
                        "version": match.group(2),
                        "type": "go",
                        "source_file": source_file
                    })
        
        return dependencies

    def calculate_code_metrics(
        self,
        files_metadata: list[dict[str, Any]]
    ) -> dict[str, Any]:
        total_files = len(files_metadata)
        total_size = sum(f.get("size", 0) for f in files_metadata)
        
        # Count files by language
        languages_breakdown = {}
        for file in files_metadata:
            lang = file.get("language")
            if lang:
                languages_breakdown[lang] = languages_breakdown.get(lang, 0) + 1
        
        # Count files by extension
        file_types = {}
        for file in files_metadata:
            ext = file.get("extension", "no_extension")
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "languages_breakdown": languages_breakdown,
            "file_types": file_types
        }

    def identify_tech_stack(
        self,
        files_metadata: list[dict[str, Any]],
        dependencies: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        tech_stack = []
        seen = set()
        
        # Identify from files
        languages = set()
        for file in files_metadata:
            lang = file.get("language")
            if lang and lang not in seen:
                languages.add(lang)
        
        for lang in languages:
            tech_stack.append({
                "name": lang,
                "category": "language",
                "version": None
            })
            seen.add(lang)
        
        # Identify from dependencies
        framework_patterns = {
            "react": ("React", "framework"),
            "vue": ("Vue.js", "framework"),
            "angular": ("Angular", "framework"),
            "express": ("Express.js", "framework"),
            "fastapi": ("FastAPI", "framework"),
            "django": ("Django", "framework"),
            "flask": ("Flask", "framework"),
            "spring": ("Spring", "framework"),
            "aspnet": ("ASP.NET", "framework"),
            "microsoft.aspnetcore": ("ASP.NET Core", "framework"),
            "entity": ("Entity Framework", "library"),
            "pytest": ("pytest", "testing"),
            "jest": ("Jest", "testing"),
            "xunit": ("xUnit", "testing"),
            "docker": ("Docker", "infrastructure"),
            "kubernetes": ("Kubernetes", "infrastructure"),
            "redis": ("Redis", "database"),
            "postgres": ("PostgreSQL", "database"),
            "mongodb": ("MongoDB", "database"),
        }
        
        for dep in dependencies:
            dep_name = dep.get("name", "").lower()
            for pattern, (name, category) in framework_patterns.items():
                if pattern in dep_name and name not in seen:
                    tech_stack.append({
                        "name": name,
                        "category": category,
                        "version": dep.get("version")
                    })
                    seen.add(name)
        
        # Check for special files
        file_names = {f.get("name", "").lower() for f in files_metadata}
        
        if "dockerfile" in file_names or "docker-compose.yml" in file_names:
            if "Docker" not in seen:
                tech_stack.append({
                    "name": "Docker",
                    "category": "infrastructure",
                    "version": None
                })
                seen.add("Docker")
        
        if ".github" in {f.get("path", "").split("/")[0] for f in files_metadata}:
            if "GitHub Actions" not in seen:
                tech_stack.append({
                    "name": "GitHub Actions",
                    "category": "ci_cd",
                    "version": None
                })
                seen.add("GitHub Actions")
        
        return tech_stack
