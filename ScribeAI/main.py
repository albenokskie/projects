#!/usr/bin/env python3
"""
Scribe - AI-powered documentation generator for Confluence
Main entry point and CLI interface.
"""

import os
import sys
import argparse
from typing import Optional

from scribe import Config, CodeAnalyzer, AIDocumentationGenerator, ConfluencePublisher
from scribe.utils import (
    convert_to_confluence_format,
    split_documentation_into_sections,
    save_preview,
    save_multi_page_preview,
    file_priority
)


class Scribe:
    """Main Scribe application"""
    
    def __init__(self, config_path: str = "scribe_config.yaml"):
        self.config = Config(config_path)
        self.analyzer = CodeAnalyzer(self.config)
        self.generator = AIDocumentationGenerator(self.config)
        self.publisher = ConfluencePublisher(self.config)
        
    def generate_docs(self, directory: str, project_name: str, space_key: Optional[str] = None, 
                     parent_id: Optional[str] = None, preview_only: bool = False, max_files: int = 50,
                     multi_page: bool = False) -> None:
        """Generate documentation for a codebase and publish to Confluence"""
        
        print(f"Analyzing codebase in: {directory}")
        print(f"Project name: {project_name}")
        print(f"Documentation mode: {'Multi-page' if multi_page else 'Single page'}")
        
        # Analyze codebase
        files = self.analyzer.analyze_directory(directory)
        
        if not files:
            print("No files found to analyze!")
            return
        
        print(f"Found {len(files)} files to analyze")
        
        # Limit files if necessary
        if len(files) > max_files:
            print(f"\n[WARNING] Found {len(files)} files, but limiting to {max_files} files to prevent timeout")
            print("You can increase this limit with --max-files option")
            
            # Sort files by importance (prioritize main files)
            files.sort(key=file_priority)
            files = files[:max_files]
            print(f"Analyzing top {len(files)} files based on priority")
        
        # Generate documentation
        print("Generating documentation with AI...")
        documentation = self.generator.generate_documentation(files, project_name)
        
        # Convert markdown to Confluence format if needed
        documentation = convert_to_confluence_format(documentation)
        
        if multi_page:
            # Split documentation into sections
            sections = split_documentation_into_sections(documentation)
            
            # Check if we have valid sections
            if not sections:
                print("\n[ERROR] Could not split documentation into sections.")
                print("The AI might not have generated proper HTML h2 headers.")
                print("Falling back to single-page mode...")
                multi_page = False
            else:
                # Preview mode for multi-page
                if preview_only or self.config.preview_before_publish:
                    save_multi_page_preview(sections, project_name)
                    
                    if preview_only:
                        print(f"Multi-page preview saved to: {project_name}_preview_multipage.html")
                        return
                    
                    # Ask for confirmation
                    response = input("\nDo you want to publish this multi-page documentation to Confluence? (y/n): ")
                    if response.lower() != 'y':
                        print("Publication cancelled.")
                        return
                
                # Publish multi-page to Confluence
                print("Publishing multi-page documentation to Confluence...")
                try:
                    result = self.publisher.publish_multi_page(
                        title=f"{project_name} - Technical Documentation",
                        sections=sections,
                        space_key=space_key,
                        parent_id=parent_id
                    )
                    
                    page_url = f"{self.config.confluence_url}/wiki/spaces/{space_key or self.config.confluence_space_key}/pages/{result['id']}"
                    print(f"\nMulti-page documentation published successfully!")
                    print(f"Main page: {page_url}")
                    
                except Exception as e:
                    print(f"Failed to publish: {e}")
                    raise
        
        if not multi_page:
            # Single page mode (existing functionality)
            # Preview mode
            if preview_only or self.config.preview_before_publish:
                save_preview(documentation, project_name)
                
                if preview_only:
                    print(f"Preview saved to: {project_name}_preview.html")
                    return
                
                # Ask for confirmation
                response = input("\nDo you want to publish this documentation to Confluence? (y/n): ")
                if response.lower() != 'y':
                    print("Publication cancelled.")
                    return
            
            # Publish to Confluence
            print("Publishing to Confluence...")
            try:
                result = self.publisher.publish(
                    title=f"{project_name} - Technical Documentation",
                    content=documentation,
                    space_key=space_key,
                    parent_id=parent_id
                )
                
                page_url = f"{self.config.confluence_url}/wiki/spaces/{space_key or self.config.confluence_space_key}/pages/{result['id']}"
                print(f"Documentation published successfully!")
                print(f"View at: {page_url}")
                
            except Exception as e:
                print(f"Failed to publish: {e}")
                raise


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Scribe - AI-powered documentation generator for Confluence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate multi-page docs for current directory (default)
  python main.py .
  
  # Generate docs under a specific parent page
  python main.py . 123456789
  
  # Generate docs for a specific project with parent ID
  python main.py /path/to/project 123456789 --name "My Project"
  
  # Generate single-page documentation
  python main.py . --single-page
  
  # Generate docs and publish to a specific Confluence space
  python main.py . --space ABC
  
  # Preview only without publishing
  python main.py . --preview-only
  
  # Use a different config file
  python main.py . --config my_config.yaml
  
  # Combine options
  python main.py ./src 123456789 --name "API Docs" --space DEV --no-preview
        """
    )
    
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('parent_id', nargs='?', help='Parent page ID in Confluence (optional)')
    parser.add_argument('--name', '-n', help='Project name (default: directory name)')
    parser.add_argument('--space', '-s', help='Confluence space key (overrides config)')
    parser.add_argument('--parent', '-p', help='Parent page ID in Confluence (alternative to positional argument)')
    parser.add_argument('--config', '-c', default='scribe_config.yaml', help='Configuration file path')
    parser.add_argument('--preview-only', action='store_true', help='Generate preview only, do not publish')
    parser.add_argument('--no-preview', action='store_true', help='Skip preview and publish directly')
    parser.add_argument('--max-files', '-m', type=int, default=50, help='Maximum number of files to analyze (default: 50)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    parser.add_argument('--single-page', action='store_true', help='Create single-page documentation instead of multi-page (default is multi-page)')
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)
    
    # Determine project name
    project_name = args.name or os.path.basename(os.path.abspath(args.directory))
    
    # Determine parent_id (positional argument takes precedence over --parent flag)
    parent_id = args.parent_id or args.parent
    
    # Determine if multi-page (default is True unless --single-page is specified)
    multi_page = not args.single_page
    
    try:
        # Initialize Scribe
        scribe = Scribe(args.config)
        
        # Override preview setting if specified
        if args.no_preview:
            scribe.config.data['settings']['preview_before_publish'] = False
        
        # Generate documentation
        scribe.generate_docs(
            directory=args.directory,
            project_name=project_name,
            space_key=args.space,
            parent_id=parent_id,
            preview_only=args.preview_only,
            max_files=args.max_files,
            multi_page=multi_page
        )
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure {args.config} exists or specify a different config file with --config")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
