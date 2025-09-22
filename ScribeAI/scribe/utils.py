"""
Scribe - AI-powered documentation generator
"""
"""Utility functions for Scribe."""

import re
from typing import Dict

from .constants import CONFLUENCE_LANGUAGE_MAP


def convert_to_confluence_format(content: str) -> str:
    """Convert markdown-style content to Confluence storage format with proper anchors"""
    
    # First, add anchors to headers for internal linking
    def add_anchor_to_header(match):
        level = len(match.group(1))
        header_text = match.group(2)
        # Create anchor ID from header text (remove special chars, lowercase, replace spaces)
        anchor_id = re.sub(r'[^\w\s-]', '', header_text).strip().lower()
        anchor_id = re.sub(r'[-\s]+', '-', anchor_id)
        
        return f'<h{level}><ac:structured-macro ac:name="anchor"><ac:parameter ac:name="">{anchor_id}</ac:parameter></ac:structured-macro>{header_text}</h{level}>'
    
    # Convert headers with anchors
    content = re.sub(r'^(#{1,6})\s+(.+)$', add_anchor_to_header, content, flags=re.MULTILINE)
    
    # Basic conversions
    conversions = [
        # Bold and italic
        (r'\*\*(.+?)\*\*', r'<strong>\1</strong>'),
        (r'\*(.+?)\*', r'<em>\1</em>'),
        
        # Code blocks
        (r'```(\w+)?\n(.*?)\n```', format_code_block, re.DOTALL),
        (r'`([^`]+)`', r'<code>\1</code>'),
        
        # Lists
        (r'^\* (.+)$', r'<li>\1</li>', re.MULTILINE),
        (r'^\d+\. (.+)$', r'<li>\1</li>', re.MULTILINE),
        
        # Internal links (e.g., [Section Name](#section-name))
        (r'\[([^\]]+)\]\(#([^)]+)\)', format_internal_link),
        
        # External links
        (r'\[([^\]]+)\]\(([^#][^)]+)\)', r'<a href="\2">\1</a>'),
        
        # Line breaks
        (r'\n\n', r'</p><p>'),
    ]
    
    # Apply conversions
    for pattern, replacement, *flags in conversions:
        if callable(replacement):
            content = re.sub(pattern, replacement, content, *flags) if flags else re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content, *flags) if flags else re.sub(pattern, replacement, content)
    
    # Wrap in paragraphs
    content = f'<p>{content}</p>'
    
    # Clean up empty paragraphs
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Fix list formatting
    content = re.sub(r'<p>(<li>.*?</li>)</p>', r'<ul>\1</ul>', content, flags=re.DOTALL)
    content = re.sub(r'</li>\s*<li>', '</li><li>', content)
    
    # Add table of contents at the beginning if there are multiple sections
    if content.count('<h2>') > 2:
        toc = '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">3</ac:parameter></ac:structured-macro>'
        # Insert TOC after the first h1 if exists, otherwise at the beginning
        if '<h1>' in content:
            content = re.sub(r'(</h1>)', r'\1\n' + toc, content, count=1)
        else:
            content = toc + '\n' + content
    
    return content


def format_internal_link(match) -> str:
    """Format internal links for Confluence"""
    link_text = match.group(1)
    anchor_id = match.group(2)
    
    return f'<ac:link ac:anchor="{anchor_id}"><ac:plain-text-link-body><![CDATA[{link_text}]]></ac:plain-text-link-body></ac:link>'


def format_code_block(match) -> str:
    """Format code blocks for Confluence"""
    language = match.group(1) or 'text'
    code = match.group(2)
    
    # Map common language names to Confluence syntax highlighting
    confluence_lang = CONFLUENCE_LANGUAGE_MAP.get(language.lower(), 'text')
    
    return f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{confluence_lang}</ac:parameter><ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body></ac:structured-macro>'


def validate_documentation_sections(sections: Dict[str, str]) -> tuple:
    """Validate that all required sections exist and have sufficient content"""
    
    required_sections = [
        "Project Overview",
        "Architecture", 
        "Installation and Setup",
        "Usage Guide",
        "API Reference",
        "Code Structure",
        "Development Guide",
        "Troubleshooting"
    ]
    
    # Check for missing sections
    missing_sections = []
    for required in required_sections:
        if required not in sections:
            missing_sections.append(required)
    
    # Check for sections with insufficient content
    incomplete_sections = []
    min_content_length = 500  # Minimum characters for a section
    
    for section_name, content in sections.items():
        # Remove HTML tags for length check
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = text_content.strip()
        
        if len(text_content) < min_content_length:
            incomplete_sections.append({
                'name': section_name,
                'length': len(text_content),
                'preview': text_content[:100] + '...' if len(text_content) > 100 else text_content
            })
    
    return missing_sections, incomplete_sections


def split_documentation_into_sections(documentation: str) -> Dict[str, str]:
    """Split documentation into sections based on h2 headers"""
    
    sections = {}
    
    # Debug: Print the documentation structure
    print("\n[DEBUG] Splitting documentation into sections...")
    
    # Find all h2 sections in the documentation
    # Updated pattern to handle both plain h2 and h2 with anchor macros
    h2_pattern = r'<h2>(?:<ac:structured-macro[^>]*>.*?</ac:structured-macro>)?\s*(.*?)\s*</h2>'
    h2_matches = list(re.finditer(h2_pattern, documentation, re.DOTALL))
    
    print(f"[DEBUG] Found {len(h2_matches)} h2 sections")
    
    if not h2_matches:
        # If no h2 headers found, there might be an issue with the AI output
        print("[DEBUG] No h2 headers found in the documentation")
        print("[DEBUG] First 500 chars of documentation:")
        print(documentation[:500])
        # Try to find any headers (h1, h2, h3) to debug
        any_header = re.findall(r'<h[1-3]>(.*?)</h[1-3]>', documentation[:1000])
        if any_header:
            print(f"[DEBUG] Found headers: {any_header}")
        
        # Return empty sections to avoid creating pages
        return {}
    
    # Skip content before the first h2 - we don't want an Overview section
    # The documentation should start directly with Project Overview
    
    # Extract each h2 section
    for i, match in enumerate(h2_matches):
        # Extract the title, removing any nested tags
        title_html = match.group(1).strip()
        # Remove any HTML tags from the title
        clean_title = re.sub(r'<[^>]+>', '', title_html)
        clean_title = clean_title.strip()
        
        if not clean_title:
            print(f"[DEBUG] Skipping empty section title at position {i}")
            continue
        
        print(f"[DEBUG] Processing section: {clean_title}")
        
        # Get content from this h2 to the next h2 (or end of document)
        start_pos = match.start()
        end_pos = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(documentation)
        
        section_content = documentation[start_pos:end_pos].strip()
        
        # Ensure we have content
        if section_content and len(section_content) > len(match.group(0)):
            sections[clean_title] = section_content
            print(f"[DEBUG] Added section: {clean_title} (length: {len(section_content)} chars)")
        else:
            print(f"[DEBUG] Skipping section {clean_title} - no content")
    
    print(f"[DEBUG] Total sections created: {len(sections)}")
    for title in sections.keys():
        print(f"  - {title}")
    
    # If we only have one or no sections, something went wrong
    if len(sections) <= 1:
        print("[WARNING] Only one or no sections found. The AI might not have generated proper h2 headers.")
        print("[WARNING] Cannot create multi-page documentation without proper sections.")
        # Try to parse the documentation differently or provide guidance
        print("\n[DEBUG] Checking for markdown headers that weren't converted...")
        markdown_headers = re.findall(r'^##\s+(.+)$', documentation, re.MULTILINE)
        if markdown_headers:
            print(f"[DEBUG] Found {len(markdown_headers)} markdown headers that weren't converted to HTML:")
            for header in markdown_headers[:5]:
                print(f"  - {header}")
            print("\n[ERROR] The AI generated markdown headers instead of HTML. The documentation needs to be in HTML format.")
        
        # Return empty to prevent creating any pages
        return {}
    
    # Validate sections
    missing_sections, incomplete_sections = validate_documentation_sections(sections)
    
    if missing_sections:
        print(f"\n[WARNING] Missing required sections:")
        for section in missing_sections:
            print(f"  - {section}")
        
        # Special handling for API Reference and Code Structure
        if "API Reference" in missing_sections:
            print("\n[WARNING] API Reference section is missing. Adding placeholder...")
            sections["API Reference"] = """<h2>API Reference</h2>
<p>This section documents the public APIs, classes, and functions in this project.</p>
<p><em>Note: The API documentation for this project needs to be generated based on the code analysis.</em></p>"""
        
        if "Code Structure" in missing_sections:
            print("\n[WARNING] Code Structure section is missing. Adding placeholder...")
            sections["Code Structure"] = """<h2>Code Structure</h2>
<p>This section provides an overview of the project's code organization.</p>
<p><em>Note: The code structure documentation for this project needs to be generated based on the file analysis.</em></p>"""
    
    if incomplete_sections:
        print(f"\n[WARNING] Sections with insufficient content (less than 500 characters):")
        for section in incomplete_sections:
            print(f"  - {section['name']} ({section['length']} chars)")
            print(f"    Preview: {section['preview']}")
    
    return sections


def save_preview(content: str, project_name: str) -> None:
    """Save a preview of the documentation"""
    
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_name} - Documentation Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{ color: #333; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        ul, ol {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <h1>{project_name} - Documentation Preview</h1>
    <hr>
    {content}
</body>
</html>"""
    
    preview_file = f"{project_name}_preview.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(preview_html)


def save_multi_page_preview(sections: Dict[str, str], project_name: str) -> None:
    """Save a preview of multi-page documentation"""
    
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_name} - Multi-Page Documentation Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{ color: #333; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        ul, ol {{ margin-left: 20px; }}
        .section {{
            border: 2px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
        }}
        .section-title {{
            background-color: #f0f0f0;
            margin: -20px -20px 20px -20px;
            padding: 10px 20px;
            border-bottom: 2px solid #ddd;
            font-weight: bold;
        }}
        .toc {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <h1>{project_name} - Multi-Page Documentation Preview</h1>
    <div class="toc">
        <h2>Table of Contents</h2>
        <p>This documentation will be split into the following pages:</p>
        <ul>"""
    
    for section_title in sections.keys():
        preview_html += f'\n            <li><a href="#{section_title.replace(" ", "-").lower()}">{section_title}</a></li>'
    
    preview_html += """
        </ul>
    </div>
    <hr>
"""
    
    for section_title, section_content in sections.items():
        section_id = section_title.replace(" ", "-").lower()
        preview_html += f"""
    <div class="section" id="{section_id}">
        <div class="section-title">Page: {project_name} - Technical Documentation - {section_title}</div>
        {section_content}
    </div>
"""
    
    preview_html += """
</body>
</html>"""
    
    preview_file = f"{project_name}_preview_multipage.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(preview_html)


def file_priority(file) -> int:
    """Calculate priority for a file based on its name"""
    from .models import FileInfo
    
    priority_names = ['readme', 'main', 'index', 'app', 'setup', 'config', '__init__']
    for i, name in enumerate(priority_names):
        if name in file.path.lower():
            return i
    return len(priority_names)
