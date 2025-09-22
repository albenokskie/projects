# Scribe Quick Start Guide

Get up and running with Scribe in 5 minutes!

## 🚀 Quick Setup

### 1. Install Python Dependencies

```bash
# Navigate to the scribe directory
cd scribe

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r 1_codex/requirements.txt
```

### 2. Configure Scribe

```bash
# Copy the template configuration
cp scribe_config_template.yaml scribe_config.yaml

# Edit the configuration file with your credentials
# (Use any text editor - notepad, vim, nano, VS Code, etc.)
```

**Required configurations:**
- Confluence URL, space key, username, and API token
- OpenAI API key (or other AI provider credentials)

### 3. Run Your First Documentation

```bash
# Generate documentation for the current directory
python 1_codex/codex.py .

# Or for a specific project
python 1_codex/codex.py /path/to/your/project
```

## 📋 Pre-flight Checklist

Before running Codex, ensure you have:

- [ ] Python 3.7+ installed (`python --version`)
- [ ] Created a Confluence API token ([Get one here](https://id.atlassian.com/manage-profile/security/api-tokens))
- [ ] Created an OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [ ] Know your Confluence space key (found in the space URL)
- [ ] Write permissions to your Confluence space

## 🎯 Common First-Time Commands

### Preview Mode (Recommended for first run)
```bash
# See what will be generated without publishing
python 1_codex/codex.py . --preview-only
```

### Small Project Test
```bash
# Analyze only 10 files to test
python 1_codex/codex.py . --max-files 10 --preview-only
```

### Specific Directory
```bash
# Document only the src folder
python 1_codex/codex.py ./src --name "Source Code Docs"
```

## 🔧 Troubleshooting First Run

### "Configuration file not found"
```bash
# Make sure you're in the right directory
ls scribe_config.yaml

# If missing, copy the template
cp scribe_config_template.yaml scribe_config.yaml
```

### "API request failed"
- Check your API keys are correct
- Verify your internet connection
- Ensure your Confluence URL includes `/wiki`

### "No files found to analyze"
- Check you're pointing to the right directory
- Verify the directory contains code files
- Review ignore patterns in config

## 📖 Next Steps

1. **Review the preview**: Open the generated HTML file to see your documentation
2. **Adjust settings**: Modify `scribe_config.yaml` to fine-tune ignore patterns
3. **Publish**: Remove `--preview-only` to publish to Confluence
4. **Explore options**: Try multi-page mode, custom names, and parent pages

## 💡 Pro Tips

- Start with `--preview-only` to see results before publishing
- Use `--max-files 20` for initial tests on large projects
- Add important context to your code comments and README files
- The better organized your code, the better the documentation

## 🆘 Need Help?

- Run with `--debug` flag for detailed output
- Check the full README.md for comprehensive documentation
- Review example commands in the main documentation

---

Ready to generate amazing documentation? Let's go! 🚀
