# Code Processor Service

AI-powered repository analysis tool that extracts comprehensive metadata from GitHub repositories using **GPT-4o**, **LangGraph**, and **GitHub API**.

## 🚀 Quick Start

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run analysis
python -m src.main --verbose

# View results
cat output.json
```

## 📊 Output Structure

The service generates `output.json` with comprehensive analysis:

### 1. Analysis Metadata
```json
{
  "analyzed_at": "2025-11-27T06:32:44.626003",
  "repository": {"owner": "...", "name": "..."},
  "analyzer_version": "1.0.0"
}
```

### 2. Repository (Enhanced)
- **repository**: Owner, name, URL
- **overview**: AI-generated summary
- **services**: All microservices/components detected (name, description, technologies, dependencies, type, port)
- **connections**: Service-to-service communication (from, to, method)
- **patterns**: Architecture patterns, communication styles
- **tech_stack**: Complete technology list

### 3. Metadata
- **files**: 500+ analyzed files with metadata
- **dependencies**: All packages (npm, pip, NuGet, etc.)
- **codeMetrics**: Statistics and metrics
- **techStack**: Technologies used

### 4. Analysis (GPT-4o Powered)
- **summary**: Executive summary
- **insights**: AI-generated insights (20+)
- **recommendations**: Actionable recommendations

### 5. Issues (GitHub)
- **summary**: Total open/closed issues and PRs
- **categorized_issues**: Bugs, features, enhancements, documentation, questions
- **metadata**: Contributors, technologies, labels, code owners
- **patterns**: Pain points, improvement opportunities, common bug areas
- **recent_activity**: Recent issues and PRs

## 🏗️ Architecture

This service analyzes GitHub repositories and generates comprehensive JSON reports containing:
- Repository metadata and file structure  
- Service-level architecture analysis
- Dependencies and technology stack
- Code metrics and quality analysis
- GitHub issues and PR analysis
- **AI-generated insights and recommendations** (powered by GPT-4o)

## 🎯 System Components

```
┌─────────────────────────────────────────────────────────┐
│              CODE PROCESSOR SERVICE                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   GitHub     │───▶│  LangGraph   │───▶│  GPT-4o   │ │
│  │   API (MCP)  │    │   Workflow   │    │    LLM    │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         │                    │                   │      │
│         └────────────────────┴───────────────────┘      │
│                              │                          │
│                    ┌─────────▼─────────┐                │
│                    │  JSON Output      │                │
│                    │  (output.json)    │                │
│                    └───────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
code-processor-service/
├── src/
│   ├── graph/                   # LangGraph Workflow
│   │   ├── workflow.py          # Orchestrates 4-node pipeline
│   │   ├── nodes.py             # Processing nodes
│   │   └── state.py             # State management
│   │
│   ├── mcp/                     # GitHub Integration
│   │   ├── client.py            # GitHub API client
│   │   └── tools.py             # MCP operations
│   │
│   ├── llm/                     # AI Integration
│   │   ├── azure_client.py      # Azure OpenAI GPT-4o client
│   │   └── prompts.py           # AI prompts
│   │
│   ├── processors/              # Data Processing
│   │   ├── metadata_extractor.py
│   │   ├── code_analyzer.py
│   │   └── json_formatter.py
│   │
│   └── main.py                  # Entry point
│
├── config/
│   ├── azure_config.json        # Azure OpenAI configuration
│   └── mcp_config.json          # MCP settings
│
├── tests/                       # Unit tests
│   ├── test_*.py
│   └── ...
│
├── .env.example                 # Environment template
├── .env                         # Your configuration (gitignored)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure OpenAI account with GPT-4o deployment
- GitHub personal access token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Rohith-Kantipudi/eShop.git
cd eShop/code-processor-service
```

2. **Create virtual environment**
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_CHAT_DEPLOYMENT
# - GITHUB_TOKEN
# - REPOSITORY_OWNER
# - REPOSITORY_NAME
```

### Configuration

Edit `.env` file with your settings:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION="2024-05-01-preview"
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o"

# GitHub Configuration
GITHUB_TOKEN="your-github-personal-access-token"

# Repository to Analyze
REPOSITORY_OWNER=Rohith-Kantipudi
REPOSITORY_NAME=eShop

# Logging
LOG_LEVEL=INFO
```

### Usage

**Basic Usage:**
```bash
python -m src.main
```

**With Verbose Output:**
```bash
python -m src.main --verbose
```

**Custom Repository:**
```bash
python -m src.main --owner USERNAME --repo REPOSITORY --output results.json
```

**Options:**
- `--owner`: Repository owner (default: from `.env`)
- `--repo`: Repository name (default: from `.env`)
- `--output`: Output file path (default: `output.json`)
- `--verbose`: Enable detailed logging

## 📊 Workflow Explanation

### The 4-Node LangGraph Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                   LANGGRAPH WORKFLOW                     │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   NODE 1     │──▶│   NODE 2     │──▶│   NODE 3     │──▶│   NODE 4     │
│  Analyze     │   │  Extract     │   │  Format &    │   │  Generate    │
│  Repository  │   │  Metadata    │   │  AI Analyze  │   │  JSON        │
│              │   │              │   │   (GPT-4o)   │   │              │
│ Uses: MCP    │   │ Uses: Parser │   │ Uses: LLM    │   │ Uses: Fmt    │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
  Fetch GitHub       Parse files      AI generates       Final JSON
  repo structure     & extract        insights &         output file
  & metadata         dependencies     recommendations
```

### Node Details

#### Node 1: Analyze Repository (MCP)
**Location:** `src/graph/nodes.py` → `analyze_repository()`

**What it does:**
1. Connects to GitHub API
2. Fetches repository information (name, languages, stars, etc.)
3. Retrieves complete file structure
4. Downloads README content

**Input:** Repository owner & name  
**Output:** Repository metadata + file list

---

#### Node 2: Extract Metadata
**Location:** `src/graph/nodes.py` → `extract_metadata()`

**What it does:**
1. Processes all files from repository
2. Extracts dependencies from:
   - `package.json` (npm)
   - `requirements.txt` (pip)
   - `*.csproj` (NuGet)
3. Calculates code metrics (file counts, languages, sizes)
4. Identifies technology stack

**Input:** File list from Node 1  
**Output:** Dependencies, metrics, tech stack

---

#### Node 3: Format & AI Analysis (LLM) 🤖
**Location:** `src/graph/nodes.py` → `format_data()`

**What it does:**
1. Sends repository data to **Azure OpenAI GPT-4o**
2. AI analyzes:
   - Architecture patterns
   - Code organization
   - Technology choices
   - Best practices
3. AI generates:
   - **Summary**: Overview of the codebase
   - **Insights**: Key observations about architecture
   - **Recommendations**: Actionable improvements

**Input:** Repository + Metadata from Nodes 1 & 2  
**Output:** AI-generated analysis

**This is where the magic happens!** GPT-4o provides intelligent insights.

---

#### Node 4: Generate JSON
**Location:** `src/graph/nodes.py` → `generate_json()`

**What it does:**
1. Combines all data from previous nodes
2. Formats into structured JSON schema
3. Writes to output file (`output.json`)

**Input:** All data from Nodes 1-3  
**Output:** Final JSON file

---

## 📄 Output Format

The service generates `output.json` with this structure:

```json
{
  "repository": {
    "name": "eShop",
    "owner": "Rohith-Kantipudi",
    "description": "...",
    "languages": ["C#", "Python", "TypeScript"],
    "structure": {
      "files": [...],
      "directories": [...]
    }
  },
  "metadata": {
    "files": [...],
    "dependencies": [
      {
        "name": "Microsoft.AspNetCore",
        "version": "9.0.0",
        "type": "nuget"
      }
    ],
    "code_metrics": {
      "total_files": 563,
      "total_size_bytes": 6261976,
      "languages_breakdown": {...}
    },
    "tech_stack": [
      {
        "name": "ASP.NET Core",
        "category": "framework",
        "version": "9.0"
      }
    ]
  },
  "analysis": {
    "summary": "AI-generated overview...",
    "insights": [
      "Microservices architecture...",
      "Event-driven design...",
      "gRPC communication..."
    ],
    "recommendations": [
      "Add comprehensive README",
      "Improve test coverage",
      "Document API endpoints"
    ]
  }
}
```

## 🔧 Components Deep Dive

### LangGraph Workflow (`src/graph/workflow.py`)

Orchestrates the entire processing pipeline using state machines:

```python
# Simplified workflow structure
workflow = StateGraph(ProcessorState)

# Add nodes
workflow.add_node("analyze_repository", nodes.analyze_repository)
workflow.add_node("extract_metadata", nodes.extract_metadata)
workflow.add_node("format_data", nodes.format_data)
workflow.add_node("generate_json", nodes.generate_json)

# Set entry point & edges
workflow.set_entry_point("analyze_repository")
workflow.add_edge("analyze_repository", "extract_metadata")
workflow.add_edge("extract_metadata", "format_data")
workflow.add_edge("format_data", "generate_json")
workflow.add_edge("generate_json", END)
```

### MCP GitHub Client (`src/mcp/client.py`)

Handles all GitHub API interactions:

```python
class GitHubMCPClient:
    async def get_repository_info(owner, repo)
    async def get_file_structure(owner, repo)
    async def get_file_content(owner, repo, path)
    async def get_repository_readme(owner, repo)
```

### Azure OpenAI LLM Client (`src/llm/azure_client.py`)

Integrates with GPT-4o for intelligent analysis:

```python
class AzureOpenAIClient:
    async def analyze_code(code, context)
    async def summarize_repository(repo_info, file_structure)
    async def extract_metadata(file_contents)
```

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name (default: gpt-4o) | No |
| `AZURE_OPENAI_API_VERSION` | API version (default: 2024-08-01-preview) | No |
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `REPOSITORY_OWNER` | Repository owner | Yes |
| `REPOSITORY_NAME` | Repository name | Yes |

### Example .env file

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
REPOSITORY_OWNER=Rohith-Kantipudi
REPOSITORY_NAME=eShop
```

## Usage

### As a Python Module

```python
import asyncio
from src.main import CodeProcessorService

async def main():
    # Initialize service
    processor = CodeProcessorService(
        repo_owner="Rohith-Kantipudi",
        repo_name="eShop"
    )
    
    # Run processing workflow
    result = await processor.process()
    
    # Get JSON output
    if result.is_complete:
        json_output = result.to_json()
        print(json_output)
        
        # Save to file
        result.save_to_file("output.json")
    else:
        print("Errors:", result.errors)

asyncio.run(main())
```

### Command Line

```bash
python -m src.main --owner Rohith-Kantipudi --repo eShop --output results.json
```

### Options

- `--owner`: Repository owner (default: from REPOSITORY_OWNER env var)
- `--repo`: Repository name (default: from REPOSITORY_NAME env var)
- `--output`: Output file path (default: output.json)
- `--verbose`: Enable verbose output

## Output Format

The service produces JSON output in the following schema:

```json
{
  "repository": {
    "name": "string",
    "owner": "string",
    "description": "string",
    "languages": ["string"],
    "defaultBranch": "string",
    "structure": {
      "totalFiles": 0,
      "totalDirectories": 0,
      "topLevelItems": ["string"]
    }
  },
  "metadata": {
    "files": [
      {
        "path": "string",
        "name": "string",
        "extension": "string",
        "size": 0,
        "language": "string"
      }
    ],
    "dependencies": [
      {
        "name": "string",
        "version": "string",
        "type": "string",
        "sourceFile": "string"
      }
    ],
    "codeMetrics": {
      "totalFiles": 0,
      "totalSizeBytes": 0,
      "languagesBreakdown": {},
      "fileTypes": {}
    },
    "techStack": [
      {
        "name": "string",
        "category": "string",
        "version": "string"
      }
    ]
  },
  "analysis": {
    "summary": "string",
    "insights": ["string"],
    "recommendations": ["string"]
  }
}
```

## Workflow Stages

The LangGraph workflow processes repositories through the following stages:

1. **Repository Analysis**: Fetches repository metadata and file structure from GitHub
2. **Metadata Extraction**: Extracts dependencies, code metrics, and technology stack
3. **Data Formatting**: Analyzes code using GPT-4o and generates insights
4. **JSON Generation**: Formats all data into the final JSON output

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

Run specific tests:

```bash
pytest tests/test_metadata_extractor.py -v
```

## 🔐 Security & Best Practices

### Environment Variables
- Never commit `.env` file to version control
- Keep API keys secure and rotate them regularly
- Use minimal GitHub token permissions (read-only for public repos)

### API Rate Limits
- **GitHub API**: 5,000 requests/hour (authenticated)
- **Azure OpenAI**: Check your quota limits
- Service includes retry logic and exponential backoff

### Error Handling
- Comprehensive error handling at each node
- Errors logged to console and stored in state
- Processing continues even if non-critical components fail

## 📈 Performance

**Typical Processing Times:**
- Small repos (<100 files): 30-60 seconds
- Medium repos (100-500 files): 1-3 minutes
- Large repos (500+ files): 3-10 minutes

**Resource Usage:**
- Memory: ~200-500 MB
- CPU: Minimal (I/O bound)
- Network: Depends on repository size

## 🐛 Troubleshooting

### Common Issues

**Issue: "GitHub token is required"**
```bash
# Solution: Set GITHUB_TOKEN in .env file
GITHUB_TOKEN="ghp_your_token_here"
```

**Issue: "Azure OpenAI endpoint is required"**
```bash
# Solution: Set Azure OpenAI credentials in .env
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

**Issue: "Failed to get repository info: 404"**
```bash
# Solution: Check repository owner and name
REPOSITORY_OWNER=correct-owner
REPOSITORY_NAME=correct-repo
```

**Issue: Rate limit exceeded**
```bash
# Solution: Wait for rate limit reset or use authenticated requests
# Check rate limit: curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

## 📚 API Reference

### Main Service

```python
from src.main import CodeProcessorService

# Initialize
service = CodeProcessorService(
    repo_owner="USERNAME",
    repo_name="REPOSITORY"
)

# Process repository
result = await service.process()

# Access results
print(result.to_json(pretty=True))
result.save_to_file("output.json")
```

### GitHub Client

```python
from src.mcp import GitHubMCPClient

client = GitHubMCPClient(github_token="...")
repo_info = await client.get_repository_info("owner", "repo")
```

### LLM Client

```python
from src.llm import AzureOpenAIClient

llm = AzureOpenAIClient()
analysis = await llm.summarize_repository(repo_info, files)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

## 📝 License

This project is part of the eShop reference application.

## 🙋 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section

## 🔄 Workflow Summary

```
START
  │
  ├─► [Node 1] Fetch GitHub Data (MCP)
  │   ↓
  │   Repository info, file structure, README
  │
  ├─► [Node 2] Extract Metadata
  │   ↓
  │   Dependencies, metrics, tech stack
  │
  ├─► [Node 3] AI Analysis (GPT-4o) 🤖
  │   ↓
  │   Summary, insights, recommendations
  │
  ├─► [Node 4] Generate JSON
  │   ↓
  │   output.json
  │
 END
```

**The entire process is automated, intelligent, and production-ready!** 🚀

---

## Quick Commands Reference

```bash
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
cp .env.example .env

# Run
python -m src.main --verbose

# Test
pytest tests/

# Check output
cat output.json
```

---

**Built with:** LangGraph • Azure OpenAI GPT-4o • GitHub API • Python 3.11+

```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Technology Stack

- **Python 3.11+**: Primary language
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM framework
- **Azure OpenAI**: GPT-4o model for analysis
- **aiohttp**: Async HTTP client for GitHub API
- **Pydantic**: Data validation
- **pytest**: Testing framework

## License

This project is part of the eShop repository and follows its licensing terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and feature requests, please use the GitHub issue tracker.
