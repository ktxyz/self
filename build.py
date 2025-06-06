import os
import re
from pathlib import Path

def convert_markdown_to_html(markdown_content):
    """Convert markdown content to HTML while preserving formatting."""
    html = markdown_content
    
    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert links [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Convert images ![alt](src)
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', html)
    
    # Convert unordered lists
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item_content = line.strip()[2:]  # Remove '- '
            result_lines.append(f'    <li>{item_content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    html = '\n'.join(result_lines)
    
    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    
    # Convert line breaks to <br> for single line breaks, preserve double line breaks as paragraphs
    lines = html.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        processed_lines.append(line)
        # Add <br> for single line breaks that aren't followed by empty lines or special elements
        if (i < len(lines) - 1 and 
            line.strip() != '' and 
            lines[i + 1].strip() != '' and
            not line.strip().startswith('<') and
            not lines[i + 1].strip().startswith('<') and
            not line.strip().startswith('#')):
            processed_lines.append('<br>')
    
    return '\n'.join(processed_lines)

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