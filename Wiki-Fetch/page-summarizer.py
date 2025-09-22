#!/usr/bin/env python3
"""
Confluence Page Summarizer
Extracts content from a specific Confluence page and creates a summary.
"""

import requests
from requests.auth import HTTPBasicAuth
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
from datetime import datetime

class ConfluencePageSummarizer:
    def __init__(self, base_url: str, username: str, api_token: str):
        """Initialize the Confluence Page Summarizer"""
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.auth = HTTPBasicAuth(username, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def extract_page_id_from_url(self, page_url: str) -> str:
        """Extract page ID from Confluence URL"""
        # Pattern for URLs like: .../pages/1370390955/Page+Title
        match = re.search(r'/pages/(\d+)/', page_url)
        if match:
            return match.group(1)
        
        # Alternative pattern
        match = re.search(r'pageId=(\d+)', page_url)
        if match:
            return match.group(1)
        
        raise ValueError("Could not extract page ID from URL")
    
    def get_page_content(self, page_id: str) -> dict:
        """Get page content from Confluence API"""
        url = f'{self.base_url}/rest/api/content/{page_id}'
        params = {
            'expand': 'body.storage,body.view,version,space,history'
        }
        
        try:
            print(f"🔍 Fetching page content for ID: {page_id}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Successfully retrieved page: {data.get('title', 'Unknown')}")
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("❌ Authentication failed - check your credentials")
            elif e.response.status_code == 403:
                print("❌ Access forbidden - you may not have permission to view this page")
            elif e.response.status_code == 404:
                print("❌ Page not found - check the page ID")
            else:
                print(f"❌ HTTP Error {e.response.status_code}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract readable text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"⚠️  Error cleaning HTML: {e}")
            return html_content
    
    def extract_structure(self, html_content: str) -> dict:
        """Extract document structure (headings, sections)"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            structure = {
                'headings': [],
                'sections': [],
                'lists': [],
                'tables': []
            }
            
            # Extract headings
            for i in range(1, 7):  # h1 to h6
                headings = soup.find_all(f'h{i}')
                for heading in headings:
                    structure['headings'].append({
                        'level': i,
                        'text': heading.get_text().strip()
                    })
            
            # Extract lists
            for ul in soup.find_all(['ul', 'ol']):
                items = [li.get_text().strip() for li in ul.find_all('li')]
                if items:
                    structure['lists'].append(items)
            
            # Extract tables
            for table in soup.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                if rows:
                    structure['tables'].append(rows)
            
            return structure
        except Exception as e:
            print(f"⚠️  Error extracting structure: {e}")
            return {}
    
    def create_summary(self, page_data: dict) -> dict:
        """Create a comprehensive summary of the page"""
        if not page_data:
            return None
        
        # Get basic page info
        summary = {
            'title': page_data.get('title', 'Unknown'),
            'page_id': page_data.get('id', 'Unknown'),
            'space': page_data.get('space', {}).get('name', 'Unknown'),
            'space_key': page_data.get('space', {}).get('key', 'Unknown'),
            'version': page_data.get('version', {}).get('number', 'Unknown'),
            'last_modified': page_data.get('version', {}).get('when', 'Unknown'),
            'created_date': page_data.get('history', {}).get('createdDate', 'Unknown'),
            'url': f"{self.base_url}/spaces/{page_data.get('space', {}).get('key', '')}/pages/{page_data.get('id', '')}",
            'content_summary': {},
            'structure': {},
            'key_points': []
        }
        
        # Process content
        if 'body' in page_data:
            if 'view' in page_data['body']:
                html_content = page_data['body']['view']['value']
                
                # Clean text content
                clean_text = self.clean_html_content(html_content)
                summary['content_summary'] = {
                    'total_characters': len(clean_text),
                    'estimated_words': len(clean_text.split()),
                    'estimated_reading_time': f"{max(1, len(clean_text.split()) // 200)} minutes"
                }
                
                # Extract structure
                summary['structure'] = self.extract_structure(html_content)
                
                # Create key points from headings and first paragraphs
                summary['key_points'] = self.extract_key_points(html_content)
                
                # Store full clean text for reference
                summary['full_text'] = clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text
        
        return summary
    
    def extract_key_points(self, html_content: str) -> list:
        """Extract key points from the content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            key_points = []
            
            # Get main headings and their following content
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                heading_text = heading.get_text().strip()
                
                # Get the next few elements after the heading
                next_content = []
                sibling = heading.find_next_sibling()
                count = 0
                
                while sibling and count < 2:  # Get next 2 elements
                    if sibling.name in ['p', 'ul', 'ol']:
                        text = sibling.get_text().strip()
                        if text and len(text) > 20:  # Only meaningful content
                            next_content.append(text[:200] + "..." if len(text) > 200 else text)
                            count += 1
                    sibling = sibling.find_next_sibling()
                
                if heading_text and next_content:
                    key_points.append({
                        'heading': heading_text,
                        'content': next_content[0] if next_content else ''
                    })
            
            return key_points[:10]  # Limit to top 10 key points
        except Exception as e:
            print(f"⚠️  Error extracting key points: {e}")
            return []
    
    def save_summary(self, summary: dict, filename: str = None):
        """Save summary to a file"""
        if not summary:
            print("❌ No summary to save")
            return
        
        if not filename:
            # Create filename from page title
            safe_title = re.sub(r'[^\w\s-]', '', summary['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_filename = f"confluence_summary_{safe_title}_{timestamp}.json"
            txt_filename = f"confluence_summary_{safe_title}_{timestamp}.txt"
        else:
            # Use provided filename and create both versions
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            json_filename = f"{base_name}.json"
            txt_filename = f"{base_name}.txt"
        
        # Save JSON file
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON summary saved to: {json_filename}")
        except Exception as e:
            print(f"❌ Error saving JSON summary: {e}")
        
        # Save text file
        try:
            self.save_summary_as_text(summary, txt_filename)
        except Exception as e:
            print(f"❌ Error saving text summary: {e}")
    
    def save_summary_as_text(self, summary: dict, filename: str):
        """Save summary as a readable text document"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("="*80 + "\n")
            f.write("CONFLUENCE PAGE SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            # Basic Information
            f.write("📄 PAGE INFORMATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Title: {summary.get('title', 'Unknown')}\n")
            f.write(f"Space: {summary.get('space', 'Unknown')} ({summary.get('space_key', 'Unknown')})\n")
            f.write(f"Page ID: {summary.get('page_id', 'Unknown')}\n")
            f.write(f"Version: {summary.get('version', 'Unknown')}\n")
            f.write(f"Last Modified: {summary.get('last_modified', 'Unknown')}\n")
            f.write(f"Created Date: {summary.get('created_date', 'Unknown')}\n")
            f.write(f"URL: {summary.get('url', 'Unknown')}\n\n")
            
            # Content Statistics
            if summary.get('content_summary'):
                cs = summary['content_summary']
                f.write("📊 CONTENT STATISTICS\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Characters: {cs.get('total_characters', 0):,}\n")
                f.write(f"Estimated Words: {cs.get('estimated_words', 0):,}\n")
                f.write(f"Estimated Reading Time: {cs.get('estimated_reading_time', 'Unknown')}\n\n")
            
            # Document Structure
            if summary.get('structure', {}).get('headings'):
                f.write("📋 DOCUMENT STRUCTURE\n")
                f.write("-" * 30 + "\n")
                for heading in summary['structure']['headings']:
                    indent = "  " * (heading['level'] - 1)
                    f.write(f"{indent}• {heading['text']}\n")
                f.write("\n")
            
            # Key Points
            if summary.get('key_points'):
                f.write("🎯 KEY POINTS\n")
                f.write("-" * 30 + "\n")
                for i, point in enumerate(summary['key_points'], 1):
                    f.write(f"{i}. {point['heading']}\n")
                    if point['content']:
                        # Format content with proper wrapping
                        content = point['content']
                        if len(content) > 200:
                            content = content[:200] + "..."
                        # Wrap long lines
                        words = content.split()
                        line = "   "
                        for word in words:
                            if len(line + word) > 75:
                                f.write(line + "\n")
                                line = "   " + word
                            else:
                                line += " " + word if line != "   " else word
                        if line.strip():
                            f.write(line + "\n")
                    f.write("\n")
            
            # Lists (if any significant ones)
            if summary.get('structure', {}).get('lists'):
                f.write("📝 IMPORTANT LISTS\n")
                f.write("-" * 30 + "\n")
                for i, lst in enumerate(summary['structure']['lists'][:3], 1):  # Show first 3 lists
                    f.write(f"List {i}:\n")
                    for item in lst[:10]:  # Show first 10 items
                        # Truncate very long items
                        display_item = item[:100] + "..." if len(item) > 100 else item
                        f.write(f"  • {display_item}\n")
                    f.write("\n")
            
            # Tables (if any)
            if summary.get('structure', {}).get('tables'):
                f.write("📊 TABLES\n")
                f.write("-" * 30 + "\n")
                for i, table in enumerate(summary['structure']['tables'][:2], 1):  # Show first 2 tables
                    f.write(f"Table {i}:\n")
                    for row in table[:5]:  # Show first 5 rows
                        f.write("  | " + " | ".join(cell[:30] + "..." if len(cell) > 30 else cell for cell in row) + " |\n")
                    f.write("\n")
            
            # Full Text Content (truncated)
            if summary.get('full_text'):
                f.write("📖 FULL TEXT CONTENT\n")
                f.write("-" * 30 + "\n")
                full_text = summary['full_text']
                
                # Break into paragraphs for better readability
                paragraphs = full_text.split('\n\n')
                for para in paragraphs[:10]:  # Show first 10 paragraphs
                    if para.strip():
                        # Wrap paragraphs to 80 characters
                        words = para.split()
                        line = ""
                        for word in words:
                            if len(line + word) > 75:
                                f.write(line + "\n")
                                line = word
                            else:
                                line += " " + word if line else word
                        if line:
                            f.write(line + "\n")
                        f.write("\n")
                
                if len(full_text) > 2000:
                    f.write("\n[Content truncated - see JSON file for complete text]\n")
            
            # Footer
            f.write("\n" + "="*80 + "\n")
            f.write(f"Summary generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Generated by Confluence Page Summarizer\n")
            f.write("="*80 + "\n")
        
        print(f"✅ Text summary saved to: {filename}")
    
    def print_summary(self, summary: dict):
        """Print a formatted summary to console"""
        if not summary:
            print("❌ No summary to display")
            return
        
        print("\n" + "="*80)
        print(f"📄 CONFLUENCE PAGE SUMMARY")
        print("="*80)
        print(f"Title: {summary['title']}")
        print(f"Space: {summary['space']} ({summary['space_key']})")
        print(f"Page ID: {summary['page_id']}")
        print(f"Version: {summary['version']}")
        print(f"Last Modified: {summary['last_modified']}")
        print(f"URL: {summary['url']}")
        
        if summary.get('content_summary'):
            cs = summary['content_summary']
            print(f"\n📊 Content Statistics:")
            print(f"   Characters: {cs.get('total_characters', 0):,}")
            print(f"   Words: {cs.get('estimated_words', 0):,}")
            print(f"   Reading Time: {cs.get('estimated_reading_time', 'Unknown')}")
        
        if summary.get('structure', {}).get('headings'):
            print(f"\n📋 Document Structure:")
            for heading in summary['structure']['headings'][:10]:
                indent = "  " * (heading['level'] - 1)
                print(f"   {indent}• {heading['text']}")
        
        if summary.get('key_points'):
            print(f"\n🎯 Key Points:")
            for i, point in enumerate(summary['key_points'][:5], 1):
                print(f"\n   {i}. {point['heading']}")
                if point['content']:
                    print(f"      {point['content'][:150]}...")
        
        print("\n" + "="*80)

def main():
    """Main function"""
    print("🚀 Confluence Page Summarizer")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    confluence_base_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_EMAIL')
    api_token = os.getenv('CONFLUENCE_TOKEN')
    
    if not all([confluence_base_url, username, api_token]):
        print("❌ Please configure your credentials in .env file")
        return
    
    # Target page URL
    page_url = "https://trendmicro.atlassian.net/wiki/spaces/aai/pages/1370390955/Codex+-+Technical+Documentation+-+Installation+and+Setup"
    
    try:
        # Initialize summarizer
        summarizer = ConfluencePageSummarizer(confluence_base_url, username, api_token)
        
        # Extract page ID
        page_id = summarizer.extract_page_id_from_url(page_url)
        print(f"📍 Extracted page ID: {page_id}")
        
        # Get page content
        page_data = summarizer.get_page_content(page_id)
        
        if page_data:
            # Create summary
            print("📝 Creating summary...")
            summary = summarizer.create_summary(page_data)
            
            # Display summary
            summarizer.print_summary(summary)
            
            # Save summary
            summarizer.save_summary(summary)
            
        else:
            print("❌ Failed to retrieve page content")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
