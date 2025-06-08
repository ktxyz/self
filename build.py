import re
import sys
from pathlib import Path
from markdown import markdown
from jinja2 import Template, Environment, FileSystemLoader


class Page:
    def __init__(self, title, slug, content):
        self.title = title
        self.slug = slug
        self.content = content

    def __repr__(self):
        return f"Page(title={self.title}, slug={self.slug})"


def load_header(header_path):
    header_file = Path(header_path)
    if not header_file.exists():
        raise FileNotFoundError(f"Header file {header_path} does not exist.")
    
    with open(header_file, "r", encoding="utf-8") as file:
        return markdown(file.read())


def load_footer(footer_path):
    footer_file = Path(footer_path)
    if not footer_file.exists():
        raise FileNotFoundError(f"Footer file {footer_path} does not exist.")
    
    with open(footer_file, "r", encoding="utf-8") as file:
        return markdown(file.read())


def parse_pages(source_dir):
    # In src directory, look for files with .md extension, recursively
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        raise FileNotFoundError(f"Source directory {source_dir} does not exist or is not a directory.")

    pages = []
    for md_file in source_path.rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Extract title from the first line
        title_match = re.match(r"#\s*(.*)", content)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = md_file.stem.replace("_", " ").title()

        # Slug is relative_path + the file name without extension
        slug = md_file.relative_to(source_path).with_suffix("").as_posix()

        print(f"Processing {md_file} -> Title: {title}, Slug: {slug}")
        pages.append(Page(title=title, slug=slug, content=content))

    return pages


def load_template(template_path, template_name):
    env = Environment(loader=FileSystemLoader(template_path))
    return env.get_template(template_name)


if __name__ == "__main__":
    pages = parse_pages("src")
    header = load_header("templates/header.md")
    footer = load_footer("templates/footer.md")
    template = load_template("templates", "base.html")

    print("Rendering pages...")
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        content = markdown(page.content, extensions=['fenced_code', 'tables'])
        if page.slug == "index":
            rendered = template.render(page_title=page.title, content=content, header=header, footer=footer, slug=page.slug, lang="en")
        else:
            rendered = template.render(page_title=page.title, content=content, header=header, footer=footer, slug=page.slug, site_title="Kamil Tokarski", lang="en")
        print(f"Rendering {page.slug}...")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{page.slug}.html"
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(rendered)
