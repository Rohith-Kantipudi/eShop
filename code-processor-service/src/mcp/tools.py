

from typing import Any, Optional

from .client import GitHubMCPClient


class MCPTools:
    def __init__(self, client: GitHubMCPClient):
        self.client = client

    async def read_repository_structure(
        self,
        owner: str,
        repo: str,
        include_content_preview: bool = False
    ) -> dict[str, Any]:
        # Get basic structure
        structure = await self.client.get_file_structure(owner, repo)
        
        # Optionally add content previews
        if include_content_preview:
            for file_info in structure.get("files", [])[:50]:  # Limit to 50 files
                if file_info.get("size", 0) < 10000:  # Only small files
                    try:
                        content = await self.client.get_file_content(
                            owner, repo, file_info["path"]
                        )
                        # Only preview first 500 chars
                        file_info["content_preview"] = content[:500]
                    except Exception:
                        pass
        
        return structure

    async def access_file_contents(
        self,
        owner: str,
        repo: str,
        paths: list[str]
    ) -> dict[str, str]:
        contents = {}
        
        for path in paths:
            try:
                content = await self.client.get_file_content(owner, repo, path)
                contents[path] = content
            except Exception as e:
                contents[path] = f"Error reading file: {str(e)}"
        
        return contents

    async def query_repository_metadata(
        self,
        owner: str,
        repo: str
    ) -> dict[str, Any]:
        repo_info = await self.client.get_repository_info(owner, repo)
        readme = await self.client.get_repository_readme(owner, repo)
        
        return {
            **repo_info,
            "readme": readme
        }

    async def search_code_semantically(
        self,
        owner: str,
        repo: str,
        queries: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        results = {}
        
        for query in queries:
            search_results = await self.client.search_code(owner, repo, query)
            results[query] = search_results
        
        return results

    async def get_dependency_files(
        self,
        owner: str,
        repo: str
    ) -> dict[str, Optional[str]]:
        dependency_files = [
            "package.json",
            "requirements.txt",
            "Pipfile",
            "pyproject.toml",
            "Gemfile",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "Directory.Packages.props",  # .NET central package management
            "*.csproj"  # .NET project files
        ]
        
        results = {}
        structure = await self.client.get_file_structure(owner, repo)
        
        for file_info in structure.get("files", []):
            file_name = file_info.get("name", "")
            file_path = file_info.get("path", "")
            
            # Check if this is a dependency file
            is_dependency_file = False
            for pattern in dependency_files:
                if pattern.startswith("*"):
                    if file_name.endswith(pattern[1:]):
                        is_dependency_file = True
                        break
                elif file_name == pattern:
                    is_dependency_file = True
                    break
            
            if is_dependency_file:
                try:
                    content = await self.client.get_file_content(
                        owner, repo, file_path
                    )
                    results[file_path] = content
                except Exception:
                    results[file_path] = None
        
        return results
