# AI Development Tools Collection

A curated collection of AI-powered development tools designed to enhance productivity and streamline workflows. This repository contains three powerful applications that leverage artificial intelligence to solve common development challenges.

## 🚀 Projects Overview

### [MetatronAI](./MetatronAI/) - Video Summarizer
A powerful command-line tool that transcribes videos and creates AI-powered summaries of the content.

**Key Features:**
- YouTube and local video processing
- AI transcription using Whisper
- Intelligent summarization with OpenAI or local models
- Chapter-based breakdowns
- Multi-language support

**Perfect for:** Educational content, meeting recordings, lecture summaries, and video documentation.

### [ScribeAI](./ScribeAI/) - Documentation Generator
An intelligent documentation generator that automatically analyzes codebases and creates comprehensive technical documentation for Confluence.

**Key Features:**
- AI-powered code analysis
- Automatic documentation generation
- Direct Confluence publishing
- Multi-page structured output
- 25+ programming language support

**Perfect for:** Technical documentation, API references, project onboarding, and maintaining up-to-date docs.

### [Wiki-Fetch](./Wiki-Fetch/) - Confluence API Client
A robust Python client for the Confluence REST API with enterprise-grade features including secure credential management and comprehensive error handling.

**Key Features:**
- Secure credential management
- Automatic retry with exponential backoff
- Rate limiting and error handling
- Comprehensive logging
- Full test coverage

**Perfect for:** Confluence automation, content migration, bulk operations, and integration workflows.

## 🛠️ Quick Start

Each project is self-contained with its own setup instructions. Navigate to the individual project directories for detailed installation and usage guides:

```bash
# Clone the repository
git clone <repository-url>
cd ai-development-tools

# Choose your project
cd MetatronAI    # For video summarization
cd ScribeAI      # For documentation generation  
cd Wiki-Fetch    # For Confluence API operations
```

## 📋 Prerequisites

- **Python 3.7+** (all projects)
- **OpenAI API Key** (MetatronAI, ScribeAI)
- **Confluence Account** (ScribeAI, Wiki-Fetch)
- **FFmpeg** (MetatronAI - auto-installed)

## 🎯 Use Cases

### Content Creation & Documentation
- **Video Content**: Summarize educational videos, meetings, and lectures with MetatronAI
- **Code Documentation**: Generate comprehensive technical docs with ScribeAI
- **Wiki Management**: Automate Confluence operations with Wiki-Fetch

### Development Workflows
- **Onboarding**: Use ScribeAI to create project documentation for new team members
- **Knowledge Management**: Combine all three tools for complete content lifecycle management
- **Automation**: Integrate Wiki-Fetch for automated documentation publishing

## 🔧 Technology Stack

- **AI/ML**: OpenAI GPT, Whisper, Hugging Face Transformers
- **APIs**: Confluence REST API, OpenAI API
- **Media Processing**: FFmpeg, PyTube
- **Languages**: Python 3.7+
- **Frameworks**: Click (CLI), Requests (HTTP), PyYAML (Config)

## 📁 Repository Structure

```
ai-development-tools/
├── MetatronAI/          # Video summarization tool
│   ├── video_summarizer/
│   ├── requirements.txt
│   └── README.md
├── ScribeAI/            # Documentation generator
│   ├── scribe/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── Wiki-Fetch/          # Confluence API client
│   ├── wiki_fetch.py
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
└── README.md           # This file
```

## 🚀 Future Projects

This repository will continue to grow with additional AI-powered development tools. Planned additions include:

- **Code Review Assistant**: AI-powered code analysis and review suggestions
- **Test Generator**: Automatic test case generation from code analysis
- **API Documentation**: Automated API documentation from code annotations
- **Deployment Assistant**: AI-guided deployment and configuration management

## 🤝 Contributing

Contributions are welcome! Each project has its own contribution guidelines. Please:

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards for each project
4. Add tests where applicable
5. Submit a pull request

## 📄 License

Each project may have its own license. Please refer to individual project directories for specific licensing information.

## 🆘 Support

For project-specific issues, please refer to the individual README files in each project directory. For general questions about the collection, feel free to open an issue.

---

**Created by Alvin Atillo (TS-PH)**

*Empowering developers with AI-powered tools for enhanced productivity and streamlined workflows.*