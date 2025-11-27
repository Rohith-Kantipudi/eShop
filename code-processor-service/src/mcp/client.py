

import os
from typing import Any, Optional

import aiohttp
from dotenv import load_dotenv

load_dotenv()


class GitHubMCPClient:
    def __init__(
        self,
        github_token: Optional[str] = None,
        mcp_server_url: Optional[str] = None
    ):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.mcp_server_url = mcp_server_url or os.getenv("MCP_SERVER_URL")
        self.base_url = "https://api.github.com"
        
        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass github_token parameter."
            )
    
    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        per_page: int = 100
    ) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            issues = []
            prs = []
            
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {"state": state, "per_page": per_page}
            
            async with session.get(url, headers=self._get_headers(), params=params) as response:
                if response.status == 200:
                    all_issues = await response.json()
                    for item in all_issues:
                        if "pull_request" in item:
                            prs.append(item)
                        else:
                            issues.append(item)
            
            return {"issues": issues, "pull_requests": prs}

    def _get_headers(self) -> dict[str, str]:
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
        async with aiohttp.ClientSession() as session:
            # Get repository metadata
            url = f"{self.base_url}/repos/{owner}/{repo}"
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get repository info: {response.status}")
                repo_data = await response.json()
            
            # Get contributors
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            async with session.get(url, headers=self._get_headers()) as response:
                contributors = await response.json() if response.status == 200 else []
            
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

    async def get_service_files(
        self,
        owner: str,
        repo: str,
        service_path: str,
        max_files: int = 10
    ) -> list[dict[str, Any]]:
        key_files = []
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{service_path}"
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status != 200:
                    return []
                
                items = await response.json()
                if not isinstance(items, list):
                    items = [items]
                
                # Smart file prioritization based on importance
                prioritized_files = []
                
                # Categorize files by importance
                for item in items:
                    if item["type"] == "file":
                        name = item["name"]
                        ext = os.path.splitext(name)[1].lower()
                        
                        # Priority scoring: higher = more important
                        priority = 0
                        
                        # Main entry points (highest priority)
                        if name.lower() in ["main", "index", "app", "server", "program", "startup", "application"]:
                            priority = 100
                        elif "main" in name.lower() or "app" in name.lower() or "server" in name.lower():
                            priority = 90
                        
                        # Configuration files
                        elif name.lower() in ["dockerfile", "docker-compose.yml", ".env", "config.json", "config.yaml", 
                                            "appsettings.json", "application.properties", "application.yml"]:
                            priority = 80
                        
                        # Package/dependency files
                        elif ext in [".json", ".toml", ".xml", ".lock", ".mod"] or name in ["gemfile", "pipfile"]:
                            priority = 70
                        
                        # Source code files
                        elif ext in [".cs", ".js", ".ts", ".py", ".java", ".go", ".rs", ".rb", ".php", ".cpp", ".c"]:
                            priority = 60
                        
                        # Documentation
                        elif ext in [".md", ".txt", ".rst"]:
                            priority = 50
                        
                        # Everything else
                        else:
                            priority = 40
                        
                        prioritized_files.append((priority, item))
                
                # Sort by priority (descending) and fetch top files
                prioritized_files.sort(key=lambda x: x[0], reverse=True)
                
                for priority, item in prioritized_files[:max_files]:
                    try:
                        content = await self.get_file_content(owner, repo, item["path"])
                        if content:
                            key_files.append({
                                "path": item["path"],
                                "name": item["name"],
                                "content": content[:5000]  # Limit to avoid token overflow
                            })
                    except Exception:
                        # Skip files that can't be read
                        continue
        
        return key_files
    
    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str
    ) -> str:
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
