import re
from typing import Dict, List, Optional

import markdown
from bs4 import BeautifulSoup, Tag
from premailer import Premailer

from markdown_parser import ImageRef, ParsedArticle
from stickers.stickers import get_sticker_html, get_section_divider
from themes import Theme, get_theme


WECHAT_MAX_CONTENT_LENGTH = 20000

STICKER_PATTERNS = {
    ":star:": "star",
    ":heart:": "heart",
    ":sparkle:": "sparkle",
    ":flower:": "flower",
    ":leaf:": "leaf",
    ":arrow:": "arrow_right",
    ":tag:": "tag",
    ":bookmark:": "bookmark",
    ":flag:": "flag",
    ":crown:": "crown",
    ":lightning:": "lightning",
    ":gift:": "gift",
    ":music:": "music_note",
    ":ribbon:": "ribbon",
    ":diamond:": "diamond",
    "::divider::": "__divider__",
}


class ContentTooLongError(Exception):
    def __init__(self, length: int, max_length: int = WECHAT_MAX_CONTENT_LENGTH):
        self.length = length
        self.max_length = max_length
        super().__init__(f"内容长度 {length} 超过限制 {max_length}")


class MarkdownConverter:
    def __init__(self, theme_name: str = "default"):
        self.theme: Theme = get_theme(theme_name)
        self.has_tables: bool = False
        self._primary_color: str = self._extract_primary_color()
        self._secondary_color: str = self._extract_secondary_color()

    def _extract_primary_color(self) -> str:
        for line in self.theme.css.splitlines():
            if "color:" in line and ".article-content h" in line:
                match = re.search(r'color:\s*(#[0-9a-fA-F]{3,8})', line)
                if match:
                    return match.group(1)
        return "#333333"

    def _extract_secondary_color(self) -> str:
        css = self.theme.css
        match = re.search(r'\.article-content\s+strong\s*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})', css, re.DOTALL)
        if match:
            return match.group(1)
        return self._primary_color

    def convert(self, article: ParsedArticle) -> str:
        md = markdown.Markdown(extensions=[
            "fenced_code",
            "tables",
            "toc",
            "nl2br",
        ])

        body = self._replace_images_with_placeholders(article.body, article.images)
        body = self._replace_stickers(body)
        html = md.convert(body)

        soup = BeautifulSoup(html, "html.parser")
        self.has_tables = len(soup.find_all("table")) > 0

        inner_html, container_style_str = self._apply_css(str(soup))

        final_html = self.theme.wrap_content(inner_html, container_style_str)

        if len(final_html) > WECHAT_MAX_CONTENT_LENGTH:
            raise ContentTooLongError(len(final_html))

        return final_html

    def _replace_stickers(self, body: str) -> str:
        result = body
        primary_color = self._primary_color
        secondary_color = self._secondary_color

        for pattern, sticker_id in STICKER_PATTERNS.items():
            if sticker_id == "__divider__":
                divider_html = get_section_divider(secondary_color)
                result = result.replace(pattern, divider_html)
            else:
                sticker_html = get_sticker_html(sticker_id, primary_color, 18)
                result = result.replace(pattern, sticker_html)

        return result

    def _replace_images_with_placeholders(self, body: str, images: List[ImageRef]) -> str:
        result = body
        for img in images:
            pattern = re.escape(img.original)
            result = re.sub(
                r"!\[([^\]]*)\]\(" + pattern + r"\)",
                f"![\\1]({img.placeholder})",
                result
            )
        return result

    def _apply_css(self, html_content: str) -> tuple[str, str]:
        html_with_class = f'<div class="article-content">{html_content}</div>'

        p = Premailer(
            html=html_with_class,
            css_text=self.theme.css,
            remove_classes=True,
            strip_important=False,
            keep_style_tags=False,
            disable_validation=True,
            disable_basic_attributes=["bgcolor"],
        )
        inline_html = p.transform()

        soup_result = BeautifulSoup(inline_html, "html.parser")

        content_div = None
        body = soup_result.find("body")
        if body:
            content_div = body.find("div", class_="article-content")
        if not content_div:
            content_div = soup_result.find("div", class_="article-content")
        if not content_div:
            content_div = soup_result.find("div")

        if not content_div:
            container_styles = self.theme._extract_container_styles()
            container_style_str = "; ".join(f"{k}: {v}" for k, v in container_styles.items())
            self.has_tables = len(soup_result.find_all("table")) > 0
            self._cleanup_attributes(soup_result)
            return str(soup_result), container_style_str

        container_style_str = content_div.get("style", "")
        if isinstance(container_style_str, list):
            container_style_str = "; ".join(container_style_str)

        del content_div["class"]
        del content_div["style"]

        inner = str(content_div)
        inner = re.sub(r'^<div>\s*', '', inner)
        inner = re.sub(r'\s*</div>$', '', inner)

        soup_out = BeautifulSoup(inner, "html.parser")
        self._cleanup_attributes(soup_out)
        self.has_tables = len(soup_out.find_all("table")) > 0

        if not container_style_str:
            container_styles = self.theme._extract_container_styles()
            container_style_str = "; ".join(f"{k}: {v}" for k, v in container_styles.items())

        return str(soup_out), container_style_str

    def _cleanup_attributes(self, container):
        for tag in container.find_all(True):
            if tag.has_attr("id"):
                del tag["id"]


def replace_image_placeholders(html: str, images: List[ImageRef]) -> str:
    result = html
    for img in images:
        if img.wechat_url:
            result = result.replace(img.placeholder, img.wechat_url)
    return result


def convert_article(article: ParsedArticle, theme_name: Optional[str] = None) -> tuple[str, MarkdownConverter]:
    theme = theme_name or article.metadata.theme
    converter = MarkdownConverter(theme)
    html = converter.convert(article)
    return html, converter