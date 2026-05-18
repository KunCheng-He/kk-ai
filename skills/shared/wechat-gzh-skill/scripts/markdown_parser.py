import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class ImageRef:
    index: int
    original: str
    placeholder: str
    wechat_url: str = ""
    is_local: bool = False


@dataclass
class ArticleMetadata:
    title: str = ""
    author: str = ""
    digest: str = ""
    cover: str = ""
    theme: str = "default"


@dataclass
class ParsedArticle:
    metadata: ArticleMetadata
    body: str
    images: List[ImageRef] = field(default_factory=list)
    source_file: Optional[str] = None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = content[match.end():]

    try:
        frontmatter = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def extract_title(body: str) -> str:
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_digest(body: str, max_len: int = 120) -> str:
    body_no_heading = re.sub(r"^#+\s+.+$", "", body, flags=re.MULTILINE)
    body_no_heading = re.sub(r"!\[.*?\]\(.*?\)", "", body_no_heading)
    body_no_heading = re.sub(r"\[.*?\]\(.*?\)", "", body_no_heading)
    body_no_heading = body_no_heading.strip()

    first_para = ""
    for line in body_no_heading.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            first_para = line
            break

    if len(first_para) > max_len:
        first_para = first_para[:max_len] + "..."

    return first_para


def extract_images(body: str) -> List[ImageRef]:
    pattern = r"!\[.*?\]\((.*?)\)"
    matches = re.findall(pattern, body)

    images = []
    for i, path in enumerate(matches):
        is_local = not path.startswith("http://") and not path.startswith("https://")
        images.append(ImageRef(
            index=i,
            original=path,
            placeholder=f"__WECHAT_IMG_PLACEHOLDER_{i}__",
            is_local=is_local
        ))

    return images


def resolve_image_path(image_path: str, source_file: Optional[str] = None) -> str:
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path

    if source_file:
        source_dir = Path(source_file).parent
        resolved = source_dir / image_path
        if resolved.exists():
            return str(resolved)

    if Path(image_path).exists():
        return image_path

    return image_path


def parse_markdown(file_path: str) -> ParsedArticle:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    content = path.read_text(encoding="utf-8")

    frontmatter, body = parse_frontmatter(content)

    title = frontmatter.get("title", "") or extract_title(body)
    author = frontmatter.get("author", "")
    digest = frontmatter.get("digest", "") or extract_digest(body)
    cover = frontmatter.get("cover", "")
    theme = frontmatter.get("theme", "default")

    metadata = ArticleMetadata(
        title=title,
        author=author,
        digest=digest,
        cover=cover,
        theme=theme,
    )

    images = extract_images(body)
    for img in images:
        if img.is_local:
            # Replace relative path with placeholder in body BEFORE resolving
            pattern = re.escape(img.original)
            body = re.sub(
                r"!\[([^\]]*)\]\(" + pattern + r"\)",
                f"![\\1]({img.placeholder})",
                body
            )
            img.original = resolve_image_path(img.original, file_path)

    return ParsedArticle(
        metadata=metadata,
        body=body,
        images=images,
        source_file=file_path,
    )


def parse_markdown_content(content: str) -> ParsedArticle:
    frontmatter, body = parse_frontmatter(content)

    title = frontmatter.get("title", "") or extract_title(body)
    author = frontmatter.get("author", "")
    digest = frontmatter.get("digest", "") or extract_digest(body)
    cover = frontmatter.get("cover", "")
    theme = frontmatter.get("theme", "default")

    metadata = ArticleMetadata(
        title=title,
        author=author,
        digest=digest,
        cover=cover,
        theme=theme,
    )

    images = extract_images(body)

    return ParsedArticle(
        metadata=metadata,
        body=body,
        images=images,
    )