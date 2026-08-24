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
    def __init__(self, theme_name: str = "ai-bubble"):
        self.theme: Theme = get_theme(theme_name)
        self.has_tables: bool = False
        self.has_code_blocks: bool = False
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
            "attr_list",
        ])

        body = self._replace_images_with_placeholders(article.body, article.images)
        body = self._replace_stickers(body)
        html = md.convert(body)

        soup = BeautifulSoup(html, "html.parser")
        self._hoist_list_classes(soup)
        self.has_tables = len(soup.find_all("table")) > 0
        self.has_code_blocks = len(soup.find_all("pre")) > 0

        inner_html, container_style_str = self._apply_css(str(soup))

        final_html = self.theme.wrap_content(inner_html, container_style_str)

        if len(final_html) > WECHAT_MAX_CONTENT_LENGTH:
            raise ContentTooLongError(len(final_html))

        return final_html

    @staticmethod
    def _hoist_list_classes(soup: BeautifulSoup) -> None:
        """Hoist a class from a lone classified <li> onto its parent list.

        Python-markdown's attr_list attaches `{: .some-class}` written after
        a list to the LAST <li> instead of the <ul>/<ol>. When exactly one
        <li> in a list carries a class (the typical attr_list idiom), move
        the class to the list element so theme CSS can target the whole
        list (e.g. `.references` for citation lists).
        """
        for list_tag in soup.find_all(["ul", "ol"]):
            classified = [
                li for li in list_tag.find_all("li", recursive=False)
                if li.get("class")
            ]
            if len(classified) == 1:
                li = classified[0]
                classes = li.get("class") or []
                if isinstance(classes, str):
                    classes = classes.split()
                existing = list_tag.get("class") or []
                if isinstance(existing, str):
                    existing = existing.split()
                list_tag["class"] = existing + classes
                del li["class"]

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
            self._wechat_safe_tables(soup_result)
            self._inject_h2_bubble(soup_result)
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
        self.has_tables = len(soup_out.find_all("table")) > 0
        self._wechat_safe_lists(soup_out, base_styles)
        self._wechat_safe_code_blocks(soup_out)
        self._wechat_safe_tables(soup_out)
        self._inject_h2_bubble(soup_out)

        if not container_style_str:
            container_styles = self.theme._extract_container_styles()
            container_style_str = "; ".join(f"{k}: {v}" for k, v in container_styles.items())

        return str(soup_out), container_style_str

    def _inject_h2_bubble(self, soup) -> None:
        """Wrap each h2 with a pure-CSS chat bubble (no SVG overlay).

        WeChat's backend sanitizer strips `position:relative/absolute`,
        which breaks SVG-overlay bubbles (the SVG loses its positioning
        context and the title text spills out of the bubble). This
        implementation draws the bubble outline with border + border-radius
        and appends a small CSS triangle tail, using only styles that
        survive WeChat's sanitization (border, border-radius, padding,
        margin, display, text-align, color).

        Only active when the theme sets h2_bubble.enabled = true.
        """
        bubble = getattr(self.theme, "h2_bubble", None)
        if not bubble or not bubble.enabled:
            return

        border = bubble.border_color
        text_color = bubble.text_color
        tail_pos = bubble.tail_position

        wrap_style = "text-align: center; margin: 40px auto 30px;"

        # Hand-drawn hook tail (logo-style J-curve) drawn as an inline SVG
        # block sibling tucked 4px under the bubble border. The SVG is NOT
        # positionally overlaid (WeChat strips position:*), it survives
        # sanitization the same way a plain block element does.
        hook_path = "M30 1 C 28 11, 21 18, 11 19 C 5 20, 1.5 16.5, 4.5 11.5"
        hook_path_right = "M4 1 C 6 11, 13 18, 23 19 C 29 20, 32.5 16.5, 29.5 11.5"
        tail_margin = {
            "left": "-4px auto 0 22px",
            "center": "-4px auto 0",
            "right": "-4px 22px 0 auto",
        }.get(tail_pos, "-4px auto 0")
        tail_path = hook_path_right if tail_pos == "right" else hook_path

        for h2 in list(soup.find_all("h2")):
            h2_style = (
                "display:inline-block; "
                f"color:{text_color}; "
                "padding:8px 20px 10px 16px; "
                "text-align:center; margin:0; "
                "box-sizing:border-box; vertical-align:top; "
                f"border:3px solid {border}; border-radius:14px 20px 16px 22px;"
            )
            existing_style = h2.get("style", "")
            if isinstance(existing_style, list):
                existing_style = "; ".join(existing_style)
            cleaned = re.sub(
                r'(border[a-z\-]*:[^;]+;?|background[a-z\-]*:[^;]+;?|'
                r'border-radius:[^;]+;?|display:[^;]+;?|'
                r'text-align:[^;]+;?|color:[^;]+;?)',
                '',
                existing_style,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(r';;+', ';', cleaned).strip('; ')
            new_style = h2_style + (("; " + cleaned) if cleaned else "")
            h2["style"] = new_style

            wrap = soup.new_tag("section")
            wrap["style"] = wrap_style

            # inline-block container so h2 + tail center as a unit and the
            # tail's margin-left offset is relative to the bubble box;
            # max-width caps very long titles at the content width
            unit = soup.new_tag("section")
            unit["style"] = "display:inline-block; max-width:100%;"

            h2.replace_with(wrap)
            unit.append(h2)

            tail = soup.new_tag("span")
            tail["style"] = f"display:block; margin:{tail_margin}; width:34px; height:22px;"
            tail_svg = BeautifulSoup(
                f'<svg width="34" height="22" viewBox="0 0 34 22" '
                f'xmlns="http://www.w3.org/2000/svg"><path d="{tail_path}" '
                f'fill="none" stroke="{border}" stroke-width="3" '
                f'stroke-linecap="round"/></svg>',
                "html.parser",
            )
            tail.append(tail_svg)
            unit.append(tail)
            wrap.append(unit)

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
            # Long lines scroll horizontally (container has overflow-x:auto).
            # If WeChat strips white-space, degrades gracefully to wrapping.
            line_styles['white-space'] = 'nowrap'
            # WeChat's editor justifies blocks without explicit text-align,
            # which would stretch code lines; pin them to left alignment.
            line_styles.setdefault('text-align', 'left')
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

    def _wechat_safe_tables(self, soup: BeautifulSoup) -> None:
        """Convert <table> markup to WeChat-proof <section> grid markup.

        WeChat's web editor normalizes foreign <table> elements whenever a
        draft is edited in the browser: the table is split into an empty
        shell (<caption>/<tfoot> placeholder rows that keep the original
        table's styles) plus a new table holding the actual rows, and the
        shell renders as empty rows at the top of the table. Converting
        tables to <section> grids styled with CSS table display
        (display: table / table-row / table-cell) sidesteps the normalizer
        entirely — the editor treats them as plain sections — while
        rendering identically to a real table.

        Zebra striping and rounded corners are applied as inline styles here
        (WeChat strips :nth-child pseudo-classes). Only tables whose theme
        sets border-radius get the bordered wrapper section and corner/zebra
        enhancements; the zebra tint derives from the border color so it
        works for any theme palette.
        """
        for table in soup.find_all('table'):
            table_styles = self._parse_inline_styles(table.get('style', ''))
            radius = table_styles.get('border-radius')

            grid_styles = {
                'display': 'table',
                'width': table_styles.get('width', '100%'),
                'border-collapse': 'separate',
                'border-spacing': '0',
            }
            if radius:
                # margin moves to the outer bordered wrapper (see below)
                grid_styles['margin'] = '0'
            elif 'margin' in table_styles:
                grid_styles['margin'] = table_styles['margin']
            grid = soup.new_tag('section')
            grid['style'] = self._build_style_string(grid_styles)

            border_color = self._extract_table_border_color(table_styles)
            zebra = (self._hex_to_rgba(border_color, 0.06)
                     if border_color else 'rgba(0, 0, 0, 0.04)')
            inner_radius = self._table_inner_radius(table_styles)

            body_row_num = 0
            last_body_cells = None
            for tr in table.find_all('tr'):
                cells = tr.find_all(['th', 'td'], recursive=False)
                if not cells:
                    continue
                is_header = bool(tr.find('th'))
                row_sec = soup.new_tag('section')
                row_sec['style'] = 'display: table-row'
                new_cells = []
                for cell in cells:
                    cell_styles = self._parse_inline_styles(cell.get('style', ''))
                    cell_sec = soup.new_tag('section')
                    cell_sec['style'] = self._build_style_string(
                        {'display': 'table-cell', **cell_styles})
                    for child in list(cell.children):
                        cell_sec.append(child.extract())
                    row_sec.append(cell_sec)
                    new_cells.append(cell_sec)
                grid.append(row_sec)

                if not radius:
                    continue
                if is_header:
                    # header row: round the top corners
                    self._set_table_cell_style(new_cells[0], 'border-top-left-radius', inner_radius)
                    self._set_table_cell_style(new_cells[-1], 'border-top-right-radius', inner_radius)
                else:
                    body_row_num += 1
                    if body_row_num % 2 == 0:
                        for cell_sec in new_cells:
                            self._set_table_cell_style(cell_sec, 'background-color', zebra)
                    last_body_cells = new_cells

            if radius and last_body_cells:
                # last row: drop the bottom rule and round the bottom corners
                for cell_sec in last_body_cells:
                    styles = self._parse_inline_styles(cell_sec.get('style', ''))
                    styles.pop('border-bottom', None)
                    cell_sec['style'] = self._build_style_string(styles)
                self._set_table_cell_style(last_body_cells[0], 'border-bottom-left-radius', inner_radius)
                self._set_table_cell_style(last_body_cells[-1], 'border-bottom-right-radius', inner_radius)

            if radius:
                # Wrap the grid in a <section> carrying the outer border,
                # radius and vertical margin
                wrap_styles = {'margin': table_styles.get('margin', '20px 0')}
                if table_styles.get('border'):
                    wrap_styles['border'] = table_styles['border']
                wrap_styles['border-radius'] = radius
                wrap_styles['overflow'] = 'hidden'
                wrapper = soup.new_tag('section')
                wrapper['style'] = self._build_style_string(wrap_styles)
                table.replace_with(wrapper)
                wrapper.append(grid)
            else:
                table.replace_with(grid)

    @staticmethod
    def _set_table_cell_style(cell: Tag, prop: str, value: str) -> None:
        """Set an inline style property on a table cell, preserving existing styles."""
        styles = MarkdownConverter._parse_inline_styles(cell.get('style', ''))
        styles[prop] = value
        cell['style'] = MarkdownConverter._build_style_string(styles)

    @staticmethod
    def _extract_table_border_color(table_styles: dict) -> Optional[str]:
        """Extract the hex color from a table border shorthand (e.g. '2px solid #2d3773')."""
        border = table_styles.get('border', '')
        match = re.search(r'#[0-9a-fA-F]{3,8}', border)
        return match.group(0) if match else None

    @staticmethod
    def _table_inner_radius(table_styles: dict) -> str:
        """Compute the cell corner radius inside the table border (radius - border width)."""
        def _px(value: str) -> Optional[int]:
            match = re.match(r'(\d+)px', value or '')
            return int(match.group(1)) if match else None

        radius = _px(table_styles.get('border-radius', ''))
        border = table_styles.get('border', '')
        width_match = re.match(r'(\d+)px', border)
        width = int(width_match.group(1)) if width_match else 0
        if radius is None:
            return '0'
        return f'{max(0, radius - width)}px'

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: float) -> str:
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'

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
            # 微信编辑器对无显式对齐的块级元素默认应用两端对齐（justify），
            # 多行列表项（如英文参考文献）词间距会被撑开，显式声明左对齐
            item_style.setdefault('text-align', 'left')
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
