"""
GitHub MCP (Model Context Protocol) client.

This module provides a client for interacting with the GitHub MCP server
to access repository information, file contents, and metadata.
"""

import os
from typing import Any, Optional

import aiohttp
from dotenv import load_dotenv

load_dotenv()


class GitHubMCPClient:
    """
    Client for GitHub MCP server interactions.
    
    This client provides methods to interact with GitHub repositories
    through the MCP protocol, including reading file structures,
    accessing contents, and querying metadata.
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        mcp_server_url: Optional[str] = None
    ):
        """
        Initialize the GitHub MCP client.
        
        Args:
            github_token: GitHub personal access token. If not provided,
                         reads from GITHUB_TOKEN environment variable.
            mcp_server_url: URL of the MCP server. If not provided,
                           reads from MCP_SERVER_URL environment variable.
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.mcp_server_url = mcp_server_url or os.getenv("MCP_SERVER_URL")
        self.base_url = "https://api.github.com"
        
        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass github_token parameter."
            )

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for GitHub API requests."""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeProcessorService"
        }

    async def get_repository_info(
        self,
        owner: str,
        repo: str
    ) -> dict[str, Any]:
        """
        Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing repository information
        """
        async with aiohttp.ClientSession() as session:
            # Get repository metadata
            url = f"{self.base_url}/repos/{owner}/{repo}"
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get repository info: {response.status}")
                repo_data = await response.json()
            
            # Get languages
            languages_url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            async with session.get(languages_url, headers=self._get_headers()) as response:
                if response.status == 200:
                    languages = list((await response.json()).keys())
                else:
                    languages = []
            
            return {
                "name": repo_data.get("name"),
                "owner": repo_data.get("owner", {}).get("login"),
                "description": repo_data.get("description"),
                "languages": languages,
                "default_branch": repo_data.get("default_branch", "main"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "topics": repo_data.get("topics", [])
            }

    async def get_file_structure(
        self,
        owner: str,
        repo: str,
        path: str = "",
        recursive: bool = True,
        max_depth: int = 3
    ) -> dict[str, Any]:
        """
        Get repository file structure.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within the repository (default: root)
            recursive: Whether to fetch recursively
            max_depth: Maximum depth for recursive fetching
            
        Returns:
            Dictionary containing file structure
        """
        files = []
        directories = []
        
        async with aiohttp.ClientSession() as session:
            await self._fetch_contents(
                session,
                owner,
                repo,
                path,
                files,
                directories,
                recursive,
                max_depth,
                current_depth=0
            )
        
        return {
            "files": files,
            "directories": directories,
            "total_files": len(files),
            "total_directories": len(directories)
        }

    async def _fetch_contents(
        self,
        session: aiohttp.ClientSession,
        owner: str,
        repo: str,
        path: str,
        files: list,
        directories: list,
        recursive: bool,
        max_depth: int,
        current_depth: int
    ) -> None:
        """Recursively fetch repository contents."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        async with session.get(url, headers=self._get_headers()) as response:
            if response.status != 200:
                return
            
            contents = await response.json()
            
            if not isinstance(contents, list):
                contents = [contents]
            
            for item in contents:
                if item["type"] == "file":
                    files.append({
                        "path": item["path"],
                        "name": item["name"],
                        "size": item.get("size", 0),
                        "sha": item.get("sha"),
                        "download_url": item.get("download_url")
                    })
                elif item["type"] == "dir":
                    directories.append({
                        "path": item["path"],
                        "name": item["name"]
                    })
                    
                    if recursive and current_depth < max_depth:
                        await self._fetch_contents(
                            session,
                            owner,
                            repo,
                            item["path"],
                            files,
                            directories,
                            recursive,
                            max_depth,
                            current_depth + 1
                        )

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str
    ) -> str:
        """
        Get the content of a specific file.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to the file
            
        Returns:
            File content as string
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get file content: {response.status}")
                
                data = await response.json()
                
                if data.get("encoding") == "base64":
                    import base64
                    try:
                        return base64.b64decode(data["content"]).decode("utf-8")
                    except (ValueError, UnicodeDecodeError) as e:
                        raise Exception(
                            f"Failed to decode base64 content for {path}: {str(e)}"
                        ) from e
                
                # Try download URL for larger files
                download_url = data.get("download_url")
                if download_url:
                    async with session.get(download_url) as dl_response:
                        return await dl_response.text()
                
                return data.get("content", "")

    async def search_code(
        self,
        owner: str,
        repo: str,
        query: str
    ) -> list[dict[str, Any]]:
        """
        Search for code in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            query: Search query
            
        Returns:
            List of matching code items
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/search/code"
            params = {
                "q": f"{query} repo:{owner}/{repo}"
            }
            
            async with session.get(
                url,
                params=params,
                headers=self._get_headers()
            ) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return data.get("items", [])

    async def get_repository_readme(
        self,
        owner: str,
        repo: str
    ) -> Optional[str]:
        """
        Get the repository README content.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content or None if not found
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/readme"
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                if data.get("encoding") == "base64":
                    import base64
                    try:
                        return base64.b64decode(data["content"]).decode("utf-8")
                    except (ValueError, UnicodeDecodeError):
                        return None
                
                return data.get("content")
