"""
Scribe - AI-powered documentation generator
"""
"""AI documentation generation module for Scribe."""

import json
import requests
import time
import logging
from typing import List

from .config import Config
from .models import FileInfo


class AIDocumentationGenerator:
    """Generates documentation using AI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def generate_documentation(self, files: List[FileInfo], project_name: str) -> str:
        """Generate comprehensive documentation for the codebase"""
        
        # Prepare the prompt
        prompt = self._create_documentation_prompt(files, project_name)
        
        # Call AI API
        try:
            response = self._call_ai_api(prompt)
            return response
        except Exception as e:
            print(f"Error generating documentation: {e}")
            raise
    
    def _create_documentation_prompt(self, files: List[FileInfo], project_name: str) -> str:
        """Create a comprehensive prompt for documentation generation"""
        
        print(f"\n[DEBUG] Creating documentation prompt:")
        print(f"  - Project name: {project_name}")
        print(f"  - Total files to analyze: {len(files)}")
        
        # Calculate total content size
        total_content_size = sum(len(file.content) for file in files)
        print(f"  - Total content size: {total_content_size:,} characters")
        
        # Group files by language
        files_by_language = {}
        for file in files:
            if file.language not in files_by_language:
                files_by_language[file.language] = []
            files_by_language[file.language].append(file)
        
        print(f"  - Languages found: {list(files_by_language.keys())}")
        for lang, lang_files in files_by_language.items():
            print(f"    - {lang}: {len(lang_files)} files")
        
        prompt = f"""You are a technical documentation expert. Generate comprehensive documentation for the '{project_name}' project based on the following codebase analysis.

Project Structure:
- Total files analyzed: {len(files)}
- Languages: {', '.join(files_by_language.keys())}

Files by language:
"""
        
        for language, lang_files in files_by_language.items():
            prompt += f"\n{language.upper()} ({len(lang_files)} files):\n"
            for file in lang_files[:10]:  # Limit to first 10 files per language for brevity
                prompt += f"  - {file.path}\n"
        
        prompt += "\n\nIMPORTANT FILES TO CONSIDER FOR DOCUMENTATION:\n"
        
        # Check for specific files that help with installation documentation
        important_files = {
            'requirements.txt': 'Python dependencies',
            'package.json': 'Node.js dependencies',
            'Gemfile': 'Ruby dependencies',
            'pom.xml': 'Maven dependencies',
            'build.gradle': 'Gradle dependencies',
            'Cargo.toml': 'Rust dependencies',
            'go.mod': 'Go dependencies',
            'composer.json': 'PHP dependencies',
            'README.md': 'Project overview',
            'INSTALL.md': 'Installation instructions',
            'setup.py': 'Python setup file',
            'Makefile': 'Build instructions',
            '.env.example': 'Environment variables',
            'config.example': 'Configuration example',
            'docker-compose.yml': 'Docker configuration'
        }
        
        found_important_files = []
        for file in files:
            filename = file.path.split('/')[-1].split('\\')[-1].lower()
            if filename in important_files or filename.endswith('.example') or filename.endswith('.sample'):
                found_important_files.append(f"- {file.path} ({important_files.get(filename, 'configuration/setup file')})")
        
        if found_important_files:
            prompt += "\nFound these important setup/configuration files:\n"
            prompt += "\n".join(found_important_files[:10])  # Limit to 10
            prompt += "\n"
        
        prompt += "\n\nCode samples for analysis:\n\n"
        
        # Include key files content (limit to prevent token overflow)
        included_files = 0
        for file in files:
            if included_files >= 35:  # Increased limit for more comprehensive analysis
                break
                
            # Prioritize certain files
            if any(name in file.path.lower() for name in ['readme', 'main', 'index', 'app', 'config', 'setup']):
                prompt += f"\n--- File: {file.path} ({file.language}) ---\n"
                prompt += file.content[:2000]  # Limit content per file
                prompt += "\n" if len(file.content) <= 2000 else "\n... (truncated)\n"
                included_files += 1
        
        # Add remaining files up to limit
        for file in files:
            if included_files >= 35:
                break
            if not any(name in file.path.lower() for name in ['readme', 'main', 'index', 'app', 'config', 'setup']):
                prompt += f"\n--- File: {file.path} ({file.language}) ---\n"
                prompt += file.content[:2000]
                prompt += "\n" if len(file.content) <= 2000 else "\n... (truncated)\n"
                included_files += 1
        
        prompt += f"""

Based on this codebase analysis, generate comprehensive technical documentation in HTML format.

CRITICAL: You MUST use HTML tags, NOT markdown. The output should be valid HTML that can be directly used in Confluence.

Generate the following sections, each starting with an <h2> tag:

<h2>Project Overview</h2>
<h3>Project Description</h3>
<p>Write a detailed 3-5 paragraph description that includes:</p>
<ul>
<li>What the project does (main functionality)</li>
<li>The problem it solves or need it addresses</li>
<li>How it works at a high level</li>
<li>What makes it unique or valuable</li>
<li>The main technologies and frameworks used</li>
</ul>
<p>Be specific and comprehensive. Include concrete details from the code analysis.</p>

<h3>Purpose and Goals</h3>
<p>Provide a thorough explanation of the project's purpose. Include:</p>
<ul>
<li>Primary objectives (list at least 3-5 specific goals)</li>
<li>Specific problems it solves (with examples)</li>
<li>Key benefits for users (be specific about value provided)</li>
<li>Business or technical value proposition</li>
</ul>

<h3>Target Audience</h3>
<p>Describe in detail who this project is intended for:</p>
<ul>
<li>Primary users (developers, end-users, administrators, etc.)</li>
<li>Required technical skill level (beginner, intermediate, advanced)</li>
<li>Prerequisites knowledge needed</li>
<li>Specific use case scenarios (provide at least 3 examples)</li>
</ul>

<h3>Key Features</h3>
<p>List ALL main features and capabilities found in the code:</p>
<ul>
<li>Core functionality (be exhaustive based on the code)</li>
<li>Notable technical features</li>
<li>Integration capabilities</li>
<li>Complete technology stack (languages, frameworks, libraries)</li>
<li>External dependencies and services used</li>
</ul>

<h2>Architecture</h2>
<h3>System Architecture</h3>
<p>Provide a comprehensive architecture overview including:</p>
<ul>
<li>Overall system design (monolithic, modular, microservices, etc.)</li>
<li>Architectural patterns used (MVC, layered, event-driven, etc.)</li>
<li>High-level component diagram description</li>
<li>Key architectural decisions and their rationale</li>
</ul>

<h3>Project Flow</h3>
<p>Describe the complete execution flow from start to finish:</p>
<ol>
<li>Initial input/trigger (what starts the process)</li>
<li>Detailed processing steps (list ALL major steps)</li>
<li>Data transformations at each step</li>
<li>Decision points and branching logic</li>
<li>Output generation and delivery</li>
<li>Error handling flow</li>
</ol>

<h3>Components and Interactions</h3>
<p>Document ALL major components found in the code:</p>
<ul>
<li>List each major class/module and its specific responsibility</li>
<li>Explain how components communicate (method calls, events, APIs)</li>
<li>Describe the data flow between components with examples</li>
<li>Identify and explain all design patterns used</li>
<li>Include dependency relationships</li>
</ul>

<h2>Installation and Setup</h2>
<p>Provide detailed installation and setup instructions based on the project structure.</p>

<h3>Prerequisites</h3>
<p>List all prerequisites needed to run this project:</p>
<ul>
<li>Required programming language version (e.g., Python 3.7+, Node.js 14+, etc.)</li>
<li>System requirements</li>
<li>External dependencies or services</li>
</ul>

<h3>Installation Steps</h3>
<p>Provide step-by-step installation instructions:</p>
<ol>
<li>How to clone or download the project</li>
<li>Navigate to the project directory</li>
<li>If there's a requirements.txt, package.json, or similar dependency file, explain how to install dependencies (e.g., pip install -r requirements.txt)</li>
<li>If virtual environment is recommended (for Python projects), explain how to create and activate it</li>
<li>Any additional setup steps specific to this project</li>
</ol>

<h3>Configuration</h3>
<p>Explain any configuration needed:</p>
<ul>
<li>If there are config files (like codex_config.yaml, .env, etc.), explain what needs to be configured</li>
<li>Provide example configuration with placeholder values</li>
<li>Explain where to get API keys or tokens if needed</li>
<li>Describe any environment variables that need to be set</li>
</ul>

<h3>Verification</h3>
<p>How to verify the installation was successful:</p>
<ul>
<li>Test commands to run</li>
<li>Expected output or behavior</li>
<li>Common installation issues and solutions</li>
</ul>

<h2>Usage Guide</h2>
<p>This section covers all the ways to use this project.</p>

<h3>Basic Usage</h3>
<p>Based on the project structure and main entry point, provide the basic usage command. For example:</p>
<ul>
<li>If there's a main.py: <code>python main.py [arguments]</code></li>
<li>If there's an index.js: <code>node index.js [arguments]</code></li>
<li>If it's a CLI tool: show the command name and basic syntax</li>
<li>If it's a library: show import and basic usage example</li>
</ul>

<h3>Command Examples</h3>
<p>Provide specific, real examples based on the actual functionality found in the code:</p>
<ul>
<li>Include the most common use cases first</li>
<li>Show examples with actual values, not just placeholders</li>
<li>If the project accepts command-line arguments, show various combinations</li>
<li>Include examples for different scenarios (development, production, testing)</li>
</ul>

<h3>Command-Line Options</h3>
<p>If the project has command-line options (check for argparse, click, or similar in Python; commander or yargs in Node.js), list them here:</p>
<table>
<tr>
<th>Option</th>
<th>Short</th>
<th>Description</th>
<th>Default</th>
<th>Example</th>
</tr>
<tr>
<td><code>--help</code></td>
<td><code>-h</code></td>
<td>Show help message</td>
<td>N/A</td>
<td><code>python main.py --help</code></td>
</tr>
<!-- Add more rows based on actual options found in the code -->
</table>

<h3>Configuration Options</h3>
<p>If the project uses configuration files, explain the available options:</p>
<ul>
<li>Configuration file format (YAML, JSON, INI, etc.)</li>
<li>Available configuration parameters</li>
<li>Example configuration with explanations</li>
</ul>

<h3>Advanced Usage</h3>
<p>Include any advanced usage patterns, such as:</p>
<ul>
<li>Using as a library/module in other projects</li>
<li>Batch processing</li>
<li>Integration with other tools</li>
<li>Automation examples</li>
</ul>

<h2>API Reference</h2>
<p>Document ALL public APIs, classes, and functions found in the code. This section MUST NOT be empty.</p>

<h3>Classes</h3>
<p>For EACH public class found in the code, provide:</p>
<ul>
<li>Class name and purpose</li>
<li>Constructor parameters</li>
<li>Public methods with parameters and return types</li>
<li>Usage example</li>
</ul>

<h3>Functions</h3>
<p>For EACH public function found in the code, provide:</p>
<ul>
<li>Function name and purpose</li>
<li>Parameters (name, type, description)</li>
<li>Return value (type and description)</li>
<li>Usage example</li>
</ul>

<h3>Modules</h3>
<p>For EACH module/package, explain:</p>
<ul>
<li>Module purpose and functionality</li>
<li>Exported functions/classes</li>
<li>Dependencies</li>
</ul>

<p>If this is a CLI tool or script with no public API, document the command-line interface instead.</p>

<h2>Code Structure</h2>
<p>Provide a complete overview of the project's code organization. This section MUST document ALL directories and key files.</p>

<h3>Directory Structure</h3>
<p>List and explain EVERY directory in the project:</p>
<pre>
project-root/
├── directory1/     # Explanation of what this directory contains
│   ├── file1.ext  # Purpose of this file
│   └── file2.ext  # Purpose of this file
├── directory2/     # Explanation
└── ...
</pre>

<h3>Key Files</h3>
<p>For EACH important file identified in the code, explain:</p>
<ul>
<li>File name and location</li>
<li>Primary purpose and functionality</li>
<li>Key classes/functions it contains</li>
<li>Dependencies and relationships with other files</li>
</ul>

<h3>Module Organization</h3>
<p>Explain how the code is organized:</p>
<ul>
<li>Package/module structure</li>
<li>Separation of concerns</li>
<li>Code organization principles used</li>
</ul>

<h2>Development Guide</h2>
<p>Comprehensive guide for developers who want to contribute or extend this project.</p>

<h3>Development Setup</h3>
<p>Steps to set up a development environment:</p>
<ol>
<li>Clone the repository</li>
<li>Install development dependencies</li>
<li>Configure development environment</li>
<li>Run tests to verify setup</li>
</ol>

<h3>Coding Standards</h3>
<p>Based on the code analysis, document the coding standards used:</p>
<ul>
<li>Code style and formatting rules</li>
<li>Naming conventions (variables, functions, classes)</li>
<li>Comment and documentation standards</li>
<li>Best practices followed in the codebase</li>
</ul>

<h3>Testing</h3>
<p>Explain the testing approach:</p>
<ul>
<li>Test framework used (if any)</li>
<li>How to run tests</li>
<li>Test coverage expectations</li>
<li>How to add new tests</li>
</ul>

<h3>Contributing</h3>
<p>How to contribute to the project:</p>
<ul>
<li>Branch naming conventions</li>
<li>Commit message format</li>
<li>Pull request process</li>
<li>Code review guidelines</li>
</ul>

<h2>Troubleshooting</h2>
<p>Common issues and their solutions based on the project structure and dependencies.</p>

<h3>Common Issues</h3>
<p>List potential issues users might encounter:</p>
<ul>
<li>Installation problems (missing dependencies, version conflicts)</li>
<li>Configuration errors (missing config files, invalid settings)</li>
<li>Runtime errors (common exceptions and their causes)</li>
<li>Performance issues (memory, CPU usage)</li>
<li>Integration problems (API connections, database issues)</li>
</ul>

<h3>Solutions</h3>
<p>For each issue above, provide:</p>
<ul>
<li>Symptoms of the problem</li>
<li>Root cause</li>
<li>Step-by-step solution</li>
<li>How to prevent it in the future</li>
</ul>

<h3>FAQ</h3>
<p>Answer frequently asked questions based on the project's functionality:</p>
<ul>
<li>How to enable debug mode</li>
<li>Where to find logs</li>
<li>How to report bugs</li>
<li>Where to get help</li>
</ul>

REMEMBER: 
- Start EVERY major section with <h2>Section Name</h2>
- Use <p> for paragraphs
- Use <ul> and <li> for bullet lists
- Use <ol> and <li> for numbered lists
- Use <code> for inline code
- Use <pre> for code blocks
- DO NOT use markdown syntax (no #, *, -, etc.)
{"Do NOT include private methods/functions (those starting with underscore) in the documentation." if not self.config.include_private else ""}
"""
        
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """Call the AI API to generate documentation with retry logic"""
        
        # Debug: Print prompt information
        prompt_size = len(prompt)
        print(f"\n[DEBUG] AI API Call Information:")
        print(f"  - Prompt size: {prompt_size} characters")
        print(f"  - Estimated tokens: ~{prompt_size // 4} tokens")
        print(f"  - Model: {self.config.ai_model}")
        print(f"  - API Endpoint: {self.config.ai_api_endpoint}")
        print(f"  - Max tokens requested: 8000")
        
        headers = {
            'Authorization': f'Bearer {self.config.ai_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.config.ai_model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a technical documentation expert. Generate clear, comprehensive, and well-structured documentation.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 8000  # Increased for more complete documentation
        }
        
        # Debug: Print request size
        request_json = json.dumps(data)
        print(f"  - Request payload size: {len(request_json)} bytes")
        
        # Retry logic with exponential backoff
        max_retries = 3
        timeout = 120  # Increased from 60 to 120 seconds
        
        for attempt in range(max_retries):
            try:
                print(f"\n[DEBUG] Attempt {attempt + 1}/{max_retries}")
                print(f"  - Timeout: {timeout} seconds")
                
                start_time = time.time()
                
                response = requests.post(
                    self.config.ai_api_endpoint,
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                
                elapsed_time = time.time() - start_time
                print(f"  - Response received in: {elapsed_time:.2f} seconds")
                print(f"  - Status code: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"AI API error: {response.status_code}"
                    try:
                        error_detail = response.json()
                        print(f"  - Error details: {json.dumps(error_detail, indent=2)}")
                        error_msg += f" - {error_detail}"
                    except:
                        print(f"  - Error response: {response.text[:500]}...")
                        error_msg += f" - {response.text}"
                    
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # 5, 10, 20 seconds
                        print(f"\n[DEBUG] Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(error_msg)
                
                # Success
                result = response.json()
                
                # Debug: Print response information
                if 'choices' in result and len(result['choices']) > 0:
                    response_content = result['choices'][0]['message']['content']
                    print(f"  - Response content length: {len(response_content)} characters")
                    print(f"  - Model used: {result.get('model', 'unknown')}")
                    
                    if 'usage' in result:
                        print(f"  - Tokens used:")
                        print(f"    - Prompt tokens: {result['usage'].get('prompt_tokens', 'N/A')}")
                        print(f"    - Completion tokens: {result['usage'].get('completion_tokens', 'N/A')}")
                        print(f"    - Total tokens: {result['usage'].get('total_tokens', 'N/A')}")
                
                return result['choices'][0]['message']['content']
                
            except requests.exceptions.Timeout:
                print(f"\n[DEBUG] Request timed out after {timeout} seconds")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    print(f"[DEBUG] Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    timeout = min(timeout * 1.5, 300)  # Increase timeout up to 5 minutes
                else:
                    print("\n[ERROR] All retry attempts failed due to timeout")
                    print("\nPossible solutions:")
                    print("1. The API might be experiencing high load - try again later")
                    print("2. Your codebase might be too large - try analyzing a smaller directory")
                    print("3. Check your internet connection")
                    print("4. Verify the API endpoint is correct and accessible")
                    raise Exception(f"API request timed out after {max_retries} attempts")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"\n[DEBUG] Connection error: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    print(f"[DEBUG] Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("\n[ERROR] Connection failed after all retry attempts")
                    print("Please check your internet connection and firewall settings")
                    raise
                    
            except Exception as e:
                print(f"\n[DEBUG] Unexpected error: {type(e).__name__}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    print(f"[DEBUG] Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
