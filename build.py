import os
import re
from pathlib import Path
from markdown import markdown

def convert_markdown_to_html(markdown_content):
    """Convert markdown content to HTML while preserving formatting."""
    html = markdown_content
    
    # Convert markdown to HTML using the markdown library
    html = markdown(html, extensions=['fenced_code', 'tables', 'toc'])

    return html

def create_html_template(title, content):
    """Create a complete HTML document with minimal styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        h1, h2, h3 {{
            margin-top: 30px;
            margin-bottom: 10px;
        }}
        h1 {{
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        hr {{
            border: none;
            border-top: 1px solid #eee;
            margin: 30px 0;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

def get_page_title(file_path, content):
    """Extract page title from markdown content or filename."""
    # Try to find the first H1 header
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    
    # Fall back to filename (without extension)
    return file_path.stem.replace('-', ' ').replace('_', ' ').title()

def build_site():
    """Build the static site."""
    src_dir = Path('src')
    dist_dir = Path('docs')
    
    # Create dist directory if it doesn't exist
    dist_dir.mkdir(exist_ok=True)
    
    # Process all markdown files
    markdown_files = list(src_dir.rglob('*.md'))
    
    if not markdown_files:
        print("No markdown files found in src directory")
        return
    
    for md_file in markdown_files:
        print(f"Processing {md_file}")
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert to HTML
        html_content = convert_markdown_to_html(markdown_content)
        
        # Get page title
        page_title = get_page_title(md_file, markdown_content)
        
        # Create complete HTML document
        full_html = create_html_template(page_title, html_content)
        
        # Calculate output path (replace .md with .html, maintain directory structure)
        relative_path = md_file.relative_to(src_dir)
        output_file = dist_dir / relative_path.with_suffix('.html')
        
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"Generated {output_file}")
    
    # Copy any other assets (images, CSS, etc.)
    for file_path in src_dir.rglob('*'):
        if file_path.is_file() and not file_path.name.endswith('.md'):
            relative_path = file_path.relative_to(src_dir)
            output_path = dist_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(file_path, output_path)
            print(f"Copied {file_path} -> {output_path}")
    
    print("Build complete!")

if __name__ == "__main__":
    build_site() 