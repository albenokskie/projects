# Scribe - AI-Powered Documentation Generator for Confluence

Scribe is an intelligent documentation generator that automatically analyzes your codebase and creates comprehensive technical documentation, then publishes it directly to Confluence. It uses AI to understand your code structure, architecture, and functionality to generate professional documentation.

## Features

- 🤖 **AI-Powered Analysis**: Uses advanced AI models to analyze and understand your codebase
- 📚 **Comprehensive Documentation**: Generates detailed technical documentation including architecture, API references, usage guides, and more
- 🔄 **Confluence Integration**: Directly publishes to Confluence with proper formatting
- 📄 **Multi-Page Support**: Creates organized multi-page documentation with parent-child structure
- 👁️ **Preview Mode**: Review generated documentation before publishing
- 🎯 **Smart File Selection**: Intelligently prioritizes important files when analyzing large codebases
- 🌐 **Multi-Language Support**: Supports 25+ programming languages including Python, JavaScript, Java, C++, Go, and more
- 🧩 **Modular Architecture**: Clean, maintainable code structure with separated concerns

## Prerequisites

- Python 3.7 or higher
- Confluence account with API access
- OpenAI API key (or compatible AI service)
- Git (optional, for repository analysis)

## Installation

1. **Clone the repository or download the files**
   ```bash
   git clone <repository-url>
   cd codex
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a configuration file**
   
   Create a `scribe_config.yaml` file in the project root with the following structure:

   ```yaml
   # Confluence settings
   confluence:
     url: "https://your-domain.atlassian.net/wiki"
     space_key: "YOUR_SPACE_KEY"
     username: "your-email@example.com"
     api_token: "your-confluence-api-token"

   # AI settings
   ai:
     model: "gpt-4"  # or gpt-3.5-turbo, claude-3, etc.
     api_key: "your-openai-api-key"
     api_endpoint: "https://api.openai.com/v1/chat/completions"

   # Documentation settings
   settings:
     ignore_patterns:
       - "*.pyc"
       - "__pycache__"
       - ".git"
       - ".venv"
       - "venv"
       - "node_modules"
       - "*.log"
       - ".DS_Store"
       - "*.tmp"
       - "build"
       - "dist"
     include_private: false  # Include private methods/functions
     max_file_size_kb: 500   # Maximum file size to analyze
     preview_before_publish: true  # Show preview before publishing
   ```

2. **Get your API credentials**
   
   - **Confluence API Token**: 
     1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
     2. Create a new API token
     3. Copy the token to your config file
   
   - **OpenAI API Key**:
     1. Go to https://platform.openai.com/api-keys
     2. Create a new API key
     3. Copy the key to your config file

## Usage

### Basic Usage

Generate documentation for the current directory:
```bash
python main.py .
```

### Command Examples

```bash
# Analyze current directory and generate multi-page documentation
python main.py .

# Generate documentation under a specific parent page
python main.py . 1360858791

# Analyze a specific project directory
python main.py /path/to/your/project

# Generate preview only without publishing
python main.py . --preview-only

# Generate single-page documentation instead of multi-page
python main.py . --single-page

# Publish to a specific Confluence space
python main.py . --space ABC

# Custom project name with parent page ID
python main.py . 1360858791 --name "My Awesome Project"

# Analyze more files (default is 50)
python main.py . --max-files 100

# Skip preview and publish directly
python main.py . --no-preview

# Use a different config file
python main.py . --config my_custom_config.yaml
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `directory` | - | Directory to analyze (required) | - |
| `parent_id` | - | Parent page ID in Confluence (optional positional) | None |
| `--name` | `-n` | Custom project name | Directory name |
| `--space` | `-s` | Confluence space key (overrides config) | From config |
| `--parent` | `-p` | Parent page ID (alternative to positional) | None |
| `--config` | `-c` | Configuration file path | scribe_config.yaml |
| `--preview-only` | - | Generate preview only, don't publish | False |
| `--no-preview` | - | Skip preview and publish directly | False |
| `--single-page` | - | Create single-page instead of multi-page | False |
| `--max-files` | `-m` | Maximum number of files to analyze | 50 |
| `--debug` | `-d` | Enable debug output | False |

## Documentation Structure

Scribe generates comprehensive documentation with the following sections:

### Multi-Page Mode (Default)
Creates a main page with child pages for each section:
- **Project Overview**: Description, purpose, target audience, key features
- **Architecture**: System design, components, data flow, patterns
- **Installation and Setup**: Prerequisites, step-by-step guide
- **Usage Guide**: Basic usage, examples, command-line options
- **API Reference**: Classes, functions, parameters, return values
- **Code Structure**: Directory layout, key files, module organization
- **Development Guide**: Contributing, coding standards, testing
- **Troubleshooting**: Common issues, FAQ, solutions

### Single-Page Mode
All sections are combined into one comprehensive page.

## Workflow

1. **Analyze**: Scribe scans your codebase, identifying key files and understanding the structure
2. **Generate**: AI analyzes the code and generates comprehensive documentation
3. **Preview**: Review the generated documentation in HTML format (optional)
4. **Publish**: Upload to Confluence with proper formatting and structure

## Tips for Best Results

1. **Organize Your Code**: Well-structured code with clear naming conventions produces better documentation
2. **Add Comments**: Include docstrings and comments in your code for more accurate documentation
3. **Use README Files**: Existing README files help provide context
4. **Configure Ignore Patterns**: Exclude test files, build artifacts, and dependencies
5. **Start Small**: For large projects, start with core modules using the `--max-files` option
6. **Review and Iterate**: Use preview mode to review and refine before publishing

## Supported Languages

Scribe recognizes and analyzes files in the following languages:
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C++ (.cpp)
- C (.c)
- C# (.cs)
- Go (.go)
- Ruby (.rb)
- PHP (.php)
- Swift (.swift)
- Kotlin (.kt)
- Rust (.rs)
- Scala (.scala)
- R (.r)
- MATLAB (.m)
- Shell/Bash (.sh)
- PowerShell (.ps1)
- YAML (.yaml, .yml)
- JSON (.json)
- XML (.xml)
- HTML (.html)
- CSS (.css)
- Markdown (.md)
- SQL (.sql)

## Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Ensure `scribe_config.yaml` exists in the current directory
   - Use `--config` to specify a different path

2. **"API request timed out"**
   - Large codebases may take time to analyze
   - Try reducing `--max-files` or analyzing specific subdirectories
   - Check your internet connection

3. **"Failed to create page: 403"**
   - Verify your Confluence API token is valid
   - Check you have write permissions to the space
   - Ensure the space key is correct

4. **"No files found to analyze"**
   - Check the directory path is correct
   - Review ignore patterns in config
   - Ensure files aren't too large (check `max_file_size_kb`)

### Debug Mode

Run with `--debug` flag for detailed output:
```bash
python main.py . --debug
```

## Security Considerations

- **API Keys**: Never commit your config file with API keys to version control
- **Private Code**: Set `include_private: false` to exclude private methods
- **Sensitive Data**: Review generated documentation before publishing
- **Access Control**: Configure Confluence page permissions appropriately

## Example Output

After running Scribe, you'll see output like:
```
Analyzing codebase in: ./my-project
Project name: my-project
Documentation mode: Multi-page
Found 45 files to analyze
Generating documentation with AI...
Multi-page preview saved to: my-project_preview_multipage.html

Do you want to publish this multi-page documentation to Confluence? (y/n): y
Publishing multi-page documentation to Confluence...
  ✓ Published section: Project Overview
  ✓ Published section: Architecture
  ✓ Published section: Installation and Setup
  ✓ Published section: Usage Guide
  ✓ Published section: API Reference
  ✓ Published section: Code Structure
  ✓ Published section: Development Guide
  ✓ Published section: Troubleshooting

Multi-page documentation published successfully!
Main page: https://your-domain.atlassian.net/wiki/spaces/YOUR_SPACE/pages/123456789
```

## Project Structure

The modular version of Scribe is organized as follows:

```
2_scribe/
├── scribe/                  # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models (FileInfo)
│   ├── constants.py       # Constants and mappings
│   ├── analyzer.py        # Code analysis functionality
│   ├── generator.py       # AI documentation generation
│   ├── publisher.py       # Confluence publishing
│   └── utils.py           # Utility functions
├── main.py                # Main entry point and CLI
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── QUICKSTART.md         # Quick start guide
└── .gitignore            # Git ignore patterns
```

### Module Descriptions

- **config.py**: Manages YAML configuration loading and provides property access to config values
- **models.py**: Contains data classes like `FileInfo` for representing code files
- **constants.py**: Defines language mappings and other constants
- **analyzer.py**: `CodeAnalyzer` class that scans directories and extracts relevant files
- **generator.py**: `AIDocumentationGenerator` class that creates documentation using AI
- **publisher.py**: `ConfluencePublisher` class that handles publishing to Confluence
- **utils.py**: Helper functions for formatting, preview generation, and documentation splitting
- **main.py**: CLI interface and main `Scribe` class that orchestrates the workflow

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Your License Here]

## Support

For issues, questions, or suggestions, please [create an issue](link-to-issues) or contact the maintainers.
