import re
from typing import Dict, List, Optional

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
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
            base_styles = self._extract_base_styles(container_style_str or container_styles)
            self._wechat_safe_lists(soup_result, base_styles)
            self._wechat_safe_code_blocks(soup_result)
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
        base_styles = self._extract_base_styles(container_style_str)
        self._wechat_safe_lists(soup_out, base_styles)
        self._wechat_safe_code_blocks(soup_out)
        self.has_tables = len(soup_out.find_all("table")) > 0

        if not container_style_str:
            container_styles = self.theme._extract_container_styles()
            container_style_str = "; ".join(f"{k}: {v}" for k, v in container_styles.items())

        return str(soup_out), container_style_str

    def _cleanup_attributes(self, container):
        for tag in container.find_all(True):
            if tag.has_attr("id"):
                del tag["id"]

    def _wechat_safe_code_blocks(self, soup: BeautifulSoup) -> None:
        """Convert <pre><code> blocks to WeChat-safe <section> markup.

        WeChat's backend editor strips white-space:pre-wrap and corrupts <pre>
        blocks, losing indentation and line breaks. This method converts each
        line of code into a separate <section> element with &nbsp; for spaces,
        ensuring formatting survives WeChat's editor.
        """
        for pre in soup.find_all('pre'):
            code_tag = pre.find('code')
            if code_tag:
                code_text = code_tag.get_text()
                code_styles = self._parse_inline_styles(code_tag.get('style', ''))
            else:
                code_text = pre.get_text()
                code_styles = {}

            pre_styles = self._parse_inline_styles(pre.get('style', ''))

            merged = dict(pre_styles)
            for prop in ('background-color', 'border-radius',
                         'font-family', 'font-size', 'color'):
                if prop in code_styles and prop not in merged:
                    merged[prop] = code_styles[prop]
            if 'padding' not in merged:
                merged['padding'] = '15px'

            container = soup.new_tag('section')
            container['style'] = self._build_style_string(merged)

            line_style_keys = ('line-height',)
            line_styles = {k: v for k, v in merged.items() if k in line_style_keys}
            if 'line-height' not in line_styles:
                line_styles['line-height'] = '1.6'
            line_style_str = self._build_style_string(line_styles)

            lines = code_text.split('\n')
            if lines and lines[-1] == '':
                lines = lines[:-1]

            for line in lines:
                line_section = soup.new_tag('section')
                line_section['style'] = line_style_str
                safe = self._preserve_indentation(line)
                if safe == '':
                    safe = '\u00a0'
                line_section.append(NavigableString(safe))
                container.append(line_section)

            pre.replace_with(container)

    @staticmethod
    def _preserve_indentation(line: str) -> str:
        """Replace leading spaces/tabs with non-breaking spaces for WeChat compatibility.

        Only leading whitespace (indentation) is replaced; mid-line spaces are
        preserved as normal spaces so word-wrapping still works.
        """
        stripped = line.lstrip(' ')
        leading_count = len(line) - len(stripped)
        result = '\u00a0' * leading_count + stripped
        result = result.replace('\t', '\u00a0\u00a0\u00a0\u00a0')
        return result

    def _wechat_safe_lists(self, soup: BeautifulSoup, base_styles: dict = None) -> None:
        """Convert <ul>/<ol>/<li> to <section> markup for WeChat editor compatibility.

        WeChat's backend editor strips/corrupts <ul>/<ol>/<li> inline styles
        when editing drafts. Converting to <section>-based markup with explicit
        bullet/number prefixes ensures formatting survives WeChat's editor.
        """
        if base_styles is None:
            base_styles = {}
        while True:
            lists = list(soup.find_all(['ul', 'ol']))
            if not lists:
                break
            processed_any = False
            for list_tag in lists:
                if not list_tag.find(['ul', 'ol']):
                    self._convert_single_list(soup, list_tag, base_styles)
                    processed_any = True
            if not processed_any:
                for list_tag in list(soup.find_all(['ul', 'ol'])):
                    self._convert_single_list(soup, list_tag, base_styles)
                break

    def _convert_single_list(self, soup: BeautifulSoup, list_tag: Tag, base_styles: dict) -> None:
        """Convert a single <ul> or <ol> element to <section> markup."""
        is_ordered = list_tag.name == 'ol'
        is_nested = list_tag.parent and list_tag.parent.name == 'li'
        list_styles = self._parse_inline_styles(list_tag.get('style', ''))

        _LIST_PROPS = ('list-style-type', 'list-style-position', 'list-style-image', 'display')
        _INHERITED_PROPS = ('font-size', 'line-height', 'font-family', 'letter-spacing', 'text-align')

        container = soup.new_tag('section')
        container_style = {}
        for prop, val in list_styles.items():
            if prop not in _LIST_PROPS and prop not in ('padding-left', 'padding'):
                container_style[prop] = val
        if not any(k.startswith('margin') for k in container_style):
            container_style['margin'] = '10px 0'
        container['style'] = self._build_style_string(container_style)

        padding_left = list_styles.get('padding-left', '25px')
        if 'padding' in list_styles:
            parts = list_styles['padding'].split()
            if len(parts) == 4:
                padding_left = parts[3]
            elif len(parts) == 2:
                padding_left = parts[1]

        if is_nested:
            padding_left = self._increase_padding(padding_left, 20)

        inherited_from_list = {}
        for prop in _INHERITED_PROPS:
            if prop in list_styles and prop not in container_style:
                inherited_from_list[prop] = list_styles[prop]

        item_num = 1
        start_attr = list_tag.get('start')
        if start_attr:
            try:
                item_num = int(start_attr)
            except (ValueError, TypeError):
                pass

        for li in list_tag.find_all('li', recursive=False):
            li_styles = self._parse_inline_styles(li.get('style', ''))

            item = soup.new_tag('section')
            item_style = {}
            for prop, val in base_styles.items():
                if prop in _INHERITED_PROPS and prop not in li_styles:
                    item_style[prop] = val
            for prop, val in inherited_from_list.items():
                if prop not in li_styles:
                    item_style[prop] = val
            for prop, val in li_styles.items():
                if prop not in _LIST_PROPS:
                    item_style[prop] = val
            if not any(k.startswith('margin') for k in item_style):
                item_style['margin'] = '5px 0'
            item_style['padding-left'] = padding_left
            item_style['text-indent'] = f'-{padding_left}'
            item['style'] = self._build_style_string(item_style)

            for p in li.find_all('p'):
                p.unwrap()

            prefix = f'{item_num}. ' if is_ordered else '• '
            item.append(NavigableString(prefix))

            for child in list(li.children):
                item.append(child.extract())

            self._strip_item_whitespace(item)

            container.append(item)
            if is_ordered:
                item_num += 1

        list_tag.replace_with(container)

    @staticmethod
    def _increase_padding(padding: str, amount: int) -> str:
        """Increase a CSS padding value by a given amount (px)."""
        match = re.match(r'(\d+)(px|em|rem)', padding)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            return f'{value + amount}{unit}'
        return padding

    @staticmethod
    def _extract_base_styles(container_style) -> dict:
        """Extract base styles (line-height, color) from container styles.
        
        Accepts either a style string or a dict, returns a dict of
        layout-critical inherited properties for WeChat compatibility.
        """
        _BASE_PROPS = ('line-height', 'color', 'letter-spacing')
        if isinstance(container_style, str):
            styles = MarkdownConverter._parse_inline_styles(container_style)
        else:
            styles = container_style
        return {k: v for k, v in styles.items() if k in _BASE_PROPS}

    @staticmethod
    def _strip_item_whitespace(item: Tag) -> None:
        """Strip leading/trailing whitespace NavigableStrings from list item section."""
        children = list(item.children)
        if not children:
            return
        first = children[0]
        if isinstance(first, NavigableString):
            first.replace_with(NavigableString(first.lstrip(' \n\t')))
        if len(children) > 1:
            last = children[-1]
            if isinstance(last, NavigableString):
                stripped = last.rstrip(' \n\t')
                if stripped:
                    last.replace_with(NavigableString(stripped))
                else:
                    last.extract()
        # Remove whitespace-only NavigableStrings between prefix and first element
        if len(children) > 1:
            second = children[1]
            if isinstance(second, NavigableString) and not second.strip():
                second.extract()

    @staticmethod
    def _parse_inline_styles(style_str: str) -> dict:
        """Parse an inline style string into a dictionary."""
        styles = {}
        if not style_str:
            return styles
        for prop in style_str.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, val = prop.split(':', 1)
                styles[key.strip()] = val.strip()
        return styles

    @staticmethod
    def _build_style_string(styles: dict) -> str:
        """Build an inline style string from a dictionary."""
        return '; '.join(f'{k}: {v}' for k, v in styles.items())


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