import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from stickers.stickers import get_sticker_html, get_section_divider


_THEMES_DIR = Path(__file__).parent / "css"

# 公众号网页编辑器中的可编辑空行（空段落），用于在装饰贴图前后
# 留出光标可定位的编辑位置
EMPTY_LINE_HTML = "<section><br/></section>"


@dataclass
class CardConfig:
    enabled: bool = False
    styles: Dict[str, str] = field(default_factory=dict)


@dataclass
class StickerConfig:
    top_decoration: Optional[str] = None
    top_decoration_color: Optional[str] = None
    top_decoration_size: int = 32
    bottom_divider: bool = False
    bottom_divider_color: Optional[str] = None


@dataclass
class BubbleConfig:
    enabled: bool = False
    border_color: str = "#2d3773"
    text_color: str = "#2d3773"
    tail_position: str = "left"  # "left" | "center" | "right"


@dataclass
class Theme:
    name: str
    description: str
    css: str
    card: CardConfig = field(default_factory=CardConfig)
    sticker: StickerConfig = field(default_factory=StickerConfig)
    h2_bubble: BubbleConfig = field(default_factory=BubbleConfig)

    def wrap_content(self, inner_html: str, container_style_str: str = "") -> str:
        parts = []

        if self.sticker.top_decoration:
            color = self.sticker.top_decoration_color or "#999"
            size = self.sticker.top_decoration_size
            # 顶部装饰前留一个可编辑空行，方便在公众号网页编辑器中
            # 将光标定位到装饰之前插入内容（如公众号名片）
            parts.append(EMPTY_LINE_HTML)
            parts.append(get_sticker_html(self.sticker.top_decoration, color, size, "block", "10px auto"))

        if self.card.enabled:
            card_style_str = "; ".join(f"{k}: {v}" for k, v in self.card.styles.items())
            parts.append(f'<section style="{card_style_str}">')
            parts.append(inner_html)
            parts.append("</section>")
        else:
            parts.append(inner_html)

        if self.sticker.bottom_divider:
            color = self.sticker.bottom_divider_color or "#999"
            # 底部分隔线前后各留一个可编辑空行，方便在公众号网页编辑器中
            # 手工插入内容（如二维码、关注引导）
            parts.append(EMPTY_LINE_HTML)
            parts.append(get_section_divider(color))
            parts.append(EMPTY_LINE_HTML)

        wrapped_inner = "\n".join(parts)

        return f'<section style="{container_style_str}">\n{wrapped_inner}\n</section>'

    def _extract_container_styles(self) -> Dict[str, str]:
        styles = {}
        match = re.search(r'\.article-content\s*\{([^}]+)\}', self.css, re.DOTALL)
        if match:
            for prop in match.group(1).split(";"):
                prop = prop.strip()
                if ":" in prop:
                    key, val = prop.split(":", 1)
                    styles[key.strip()] = val.strip()
        return styles


def _load_theme_meta(theme_name: str) -> dict:
    yaml_path = _THEMES_DIR / f"{theme_name}.yaml"
    if not yaml_path.exists():
        return {}
    return yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}


def _load_theme_css(theme_name: str) -> str:
    css_path = _THEMES_DIR / f"{theme_name}.css"
    if not css_path.exists():
        raise FileNotFoundError(f"主题 CSS 文件不存在: {css_path}")
    return css_path.read_text(encoding="utf-8")


def get_theme(theme_name: str) -> Theme:
    if theme_name not in list_themes():
        available = ", ".join(list_themes().keys())
        raise ValueError(f"未知主题: {theme_name}，可用主题: {available}")

    meta = _load_theme_meta(theme_name)
    css = _load_theme_css(theme_name)

    card_config = CardConfig(enabled=False, styles={})
    card_data = meta.get("card")
    if card_data and card_data.get("enabled"):
        card_config.enabled = True
        for key in ("max-width", "margin", "padding", "background-color",
                     "border-radius", "border", "box-shadow"):
            if key in card_data:
                card_config.styles[key] = card_data[key]

    sticker_config = StickerConfig()
    sticker_data = meta.get("sticker")
    if sticker_data:
        sticker_config.top_decoration = sticker_data.get("top_decoration")
        sticker_config.top_decoration_color = sticker_data.get("top_decoration_color")
        sticker_config.top_decoration_size = sticker_data.get("top_decoration_size", 32)
        sticker_config.bottom_divider = sticker_data.get("bottom_divider", False)
        sticker_config.bottom_divider_color = sticker_data.get("bottom_divider_color")

    bubble_config = BubbleConfig()
    bubble_data = meta.get("h2_bubble")
    if bubble_data and bubble_data.get("enabled"):
        bubble_config.enabled = True
        bubble_config.border_color = bubble_data.get("border_color", "#2d3773")
        bubble_config.text_color = bubble_data.get("text_color", "#2d3773")
        bubble_config.tail_position = bubble_data.get("tail_position", "left")

    return Theme(
        name=meta.get("name", theme_name),
        description=meta.get("description", theme_name),
        css=css,
        card=card_config,
        sticker=sticker_config,
        h2_bubble=bubble_config,
    )


def list_themes() -> Dict[str, str]:
    themes = {}
    for css_file in sorted(_THEMES_DIR.glob("*.css")):
        theme_name = css_file.stem
        meta = _load_theme_meta(theme_name)
        themes[theme_name] = meta.get("description", theme_name)
    return themes
