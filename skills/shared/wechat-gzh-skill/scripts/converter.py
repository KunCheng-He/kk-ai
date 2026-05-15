import re
from typing import Dict, List, Optional

import markdown
from bs4 import BeautifulSoup, Tag

from markdown_parser import ImageRef, ParsedArticle
from themes import get_theme


WECHAT_MAX_CONTENT_LENGTH = 20000


class ContentTooLongError(Exception):
    def __init__(self, length: int, max_length: int = WECHAT_MAX_CONTENT_LENGTH):
        self.length = length
        self.max_length = max_length
        super().__init__(f"内容长度 {length} 超过限制 {max_length}")


class MarkdownConverter:
    def __init__(self, theme_name: str = "default"):
        self.theme = get_theme(theme_name)
        self.has_tables: bool = False

    def convert(self, article: ParsedArticle) -> str:
        md = markdown.Markdown(extensions=[
            "fenced_code",
            "tables",
            "toc",
            "nl2br",
        ])

        body = self._replace_images_with_placeholders(article.body, article.images)
        html = md.convert(body)

        soup = BeautifulSoup(html, "html.parser")

        self.has_tables = len(soup.find_all("table")) > 0

        self._apply_styles(soup)

        styled_html = str(soup)

        final_html = self.theme.wrap_content(styled_html)

        if len(final_html) > WECHAT_MAX_CONTENT_LENGTH:
            raise ContentTooLongError(len(final_html))

        return final_html

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

    def _apply_styles(self, soup: BeautifulSoup):
        for tag in soup.find_all(True):
            if not isinstance(tag, Tag):
                continue

            tag_name = tag.name

            if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                self._style_heading(tag)
            elif tag_name == "p":
                self._style_paragraph(tag)
            elif tag_name == "blockquote":
                self._style_blockquote(tag)
            elif tag_name == "pre":
                self._style_code_block(tag)
            elif tag_name == "code":
                self._style_inline_code(tag)
            elif tag_name == "img":
                self._style_image(tag)
            elif tag_name == "ul" or tag_name == "ol":
                self._style_list(tag)
            elif tag_name == "li":
                self._style_list_item(tag)
            elif tag_name == "table":
                self._style_table(tag)
            elif tag_name == "hr":
                self._style_hr(tag)
            elif tag_name == "strong":
                self._style_strong(tag)
            elif tag_name == "em":
                self._style_em(tag)
            elif tag_name == "a":
                self._style_link(tag)

    def _style_heading(self, tag: Tag):
        level = int(tag.name[1])
        styles = self.theme.get_heading_style(level)
        tag["style"] = self._dict_to_style(styles)

    def _style_paragraph(self, tag: Tag):
        styles = self.theme.get_paragraph_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_blockquote(self, tag: Tag):
        styles = self.theme.get_blockquote_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_code_block(self, tag: Tag):
        styles = self.theme.get_code_block_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_inline_code(self, tag: Tag):
        if tag.parent and tag.parent.name == "pre":
            return
        styles = self.theme.get_inline_code_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_image(self, tag: Tag):
        styles = self.theme.get_image_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_list(self, tag: Tag):
        styles = self.theme.get_list_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_list_item(self, tag: Tag):
        styles = self.theme.get_list_item_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_table(self, tag: Tag):
        styles = self.theme.get_table_style()
        tag["style"] = self._dict_to_style(styles)
        for td in tag.find_all("td"):
            td["style"] = self._dict_to_style(self.theme.get_table_cell_style())
        for th in tag.find_all("th"):
            th["style"] = self._dict_to_style(self.theme.get_table_header_style())

    def _style_hr(self, tag: Tag):
        styles = self.theme.get_hr_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_strong(self, tag: Tag):
        styles = self.theme.get_strong_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_em(self, tag: Tag):
        styles = self.theme.get_em_style()
        tag["style"] = self._dict_to_style(styles)

    def _style_link(self, tag: Tag):
        styles = self.theme.get_link_style()
        tag["style"] = self._dict_to_style(styles)

    def _dict_to_style(self, styles: Dict[str, str]) -> str:
        return "; ".join(f"{k}: {v}" for k, v in styles.items())


def replace_image_placeholders(html: str, images: List[ImageRef]) -> str:
    result = html
    for img in images:
        if img.wechat_url:
            placeholder_pattern = re.escape(img.placeholder)
            img_tag = f'<img src="{img.wechat_url}" style="max-width:100%;height:auto;display:block;margin:20px auto;" />'
            result = re.sub(placeholder_pattern, img.wechat_url, result)
    return result


def convert_article(article: ParsedArticle, theme_name: Optional[str] = None) -> tuple[str, MarkdownConverter]:
    theme = theme_name or article.metadata.theme
    converter = MarkdownConverter(theme)
    html = converter.convert(article)
    return html, converter
