# Code Processor Service

A Python service that uses LangGraph to extract and process metadata from GitHub repositories, formatting the output as JSON and leveraging Azure OpenAI GPT-4o for intelligent analysis.

## Features

- **LangGraph Workflow**: Orchestrates the code processing pipeline with conditional routing
- **GitHub MCP Integration**: Accesses repository structure, files, and metadata
- **Azure OpenAI GPT-4o**: Provides intelligent code analysis and summarization
- **Comprehensive Metadata Extraction**: Extracts dependencies, code metrics, and tech stack
- **Structured JSON Output**: Formats results in a consistent, well-defined schema

## Architecture

```
code-processor-service/
├── src/
│   ├── graph/
│   │   ├── workflow.py          # LangGraph workflow definition
│   │   ├── nodes.py             # Processing nodes
│   │   └── state.py             # State definitions
│   ├── mcp/
│   │   ├── client.py            # GitHub MCP client
│   │   └── tools.py             # MCP tool wrappers
│   ├── llm/
│   │   ├── azure_client.py      # Azure OpenAI client
│   │   └── prompts.py           # LLM prompts
│   ├── processors/
│   │   ├── metadata_extractor.py
│   │   ├── code_analyzer.py
│   │   └── json_formatter.py
│   └── main.py                  # Entry point
├── config/
│   ├── azure_config.json
│   └── mcp_config.json
├── tests/
├── requirements.txt
├── README.md
└── .env.example
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rohith-Kantipudi/eShop.git
cd eShop/code-processor-service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
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
