from typing import Dict

from themes.base import BaseTheme
from stickers.stickers import (
    get_sticker_html, get_title_decorations, 
    get_section_divider, get_tip_box_icon, get_important_mark
)


class XiumiStyleTheme(BaseTheme):
    """
    秀米风格主题
    特点：丰富的 SVG 贴图装饰、卡片式布局、柔和配色
    """
    name = "xiumi-style"
    description = "秀米风格，丰富 SVG 贴图装饰 + 卡片式布局 + 柔和配色，适合教程、分享、笔记"

    colors = {
        "background": "#f8faf8",
        "card_bg": "#ffffff",
        "text": "#2d3a2e",
        "primary": "#3d7a4a",
        "secondary": "#5a9b6b",
        "tertiary": "#8bc99a",
        "accent": "#2e6b3a",
        "subtitle": "#5a6b5c",
        "quote_bg": "#f0f7f1",
        "code_bg": "#f4f8f4",
        "border": "rgba(61, 122, 74, 0.12)",
        "shadow": "rgba(61, 122, 74, 0.05)",
    }

    typography = {
        "font_family": "'PingFang SC', system-ui, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif",
        "font_size": "15px",
        "line_height": "1.8",
        "letter_spacing": "0.3px",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "25px 10px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
            "letter-spacing": self.typography["letter_spacing"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "22px", 2: "19px", 3: "17px", 4: "16px", 5: "15px", 6: "14px"}
        
        if level == 1:
            # 一级标题：带装饰的卡片式
            return {
                "font-size": sizes.get(level, "18px"),
                "font-weight": "bold",
                "color": self.colors["primary"],
                "background": f"linear-gradient(135deg, {self.colors['card_bg']} 0%, {self.colors['quote_bg']} 100%)",
                "display": "block",
                "padding": "16px 20px",
                "border-radius": "12px",
                "margin": "25px 0 15px",
                "border-left": f"4px solid {self.colors['primary']}",
                "box-shadow": f"0 2px 8px {self.colors['shadow']}",
            }
        elif level == 2:
            # 二级标题：带图标
            return {
                "font-size": sizes.get(level, "17px"),
                "font-weight": "bold",
                "color": self.colors["secondary"],
                "display": "flex",
                "align-items": "center",
                "gap": "8px",
                "margin": "20px 0 12px",
                "padding": "8px 0",
                "border-bottom": f"2px dashed {self.colors['tertiary']}",
            }
        elif level == 3:
            # 三级标题：简洁带前缀
            return {
                "font-size": sizes.get(level, "16px"),
                "font-weight": "600",
                "color": self.colors["accent"],
                "margin": "15px 0 10px",
                "padding-left": "12px",
                "border-left": f"3px solid {self.colors['tertiary']}",
            }
        else:
            return {
                "font-size": sizes.get(level, "15px"),
                "font-weight": "600",
                "color": self.colors["text"],
                "margin": "12px 0 8px",
            }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 8px",
            "text-align": "justify",
            "color": self.colors["text"],
            "line-height": "1.8em",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        # 引用块带装饰图标
        return {
            "margin": "18px 8px",
            "padding": "16px 20px",
            "background-color": self.colors["quote_bg"],
            "border-radius": "12px",
            "border": f"1px solid {self.colors['border']}",
            "color": self.colors["subtitle"],
            "font-size": "14px",
            "line-height": "1.7em",
            "position": "relative",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 8px",
            "padding": "16px",
            "background-color": self.colors["code_bg"],
            "border-radius": "10px",
            "overflow-x": "auto",
            "font-family": "'Fira Code', Consolas, Monaco, 'Courier New', monospace",
            "font-size": "13px",
            "border": f"1px solid {self.colors['border']}",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 8px",
            "background-color": self.colors["quote_bg"],
            "border-radius": "6px",
            "font-family": "'Fira Code', Consolas, Monaco, 'Courier New', monospace",
            "font-size": "13px",
            "color": self.colors["primary"],
        }

    def get_image_style(self) -> Dict[str, str]:
        return {
            "max-width": "100%",
            "height": "auto",
            "display": "block",
            "margin": "15px auto",
            "border-radius": "10px",
            "box-shadow": f"0 4px 12px {self.colors['shadow']}",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 8px",
            "padding-left": "20px",
            "line-height": "1.8em",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "6px 0",
            "color": self.colors["text"],
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "15px 8px",
            "border-collapse": "separate",
            "border-spacing": "0",
            "border-radius": "10px",
            "overflow": "hidden",
            "box-shadow": f"0 2px 8px {self.colors['shadow']}",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "10px 14px",
            "border": f"1px solid {self.colors['border']}",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "10px 14px",
            "border": f"1px solid {self.colors['border']}",
            "background-color": self.colors["quote_bg"],
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "height": "1px",
            "background": f"linear-gradient(to right, transparent, {self.colors['tertiary']}, transparent)",
            "margin": "25px 8px",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": self.colors["secondary"],
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["accent"],
            "text-decoration": "none",
            "border-bottom": f"1px dotted {self.colors['accent']}",
        }

    def wrap_content(self, html: str) -> str:
        """包装内容，添加整体卡片容器"""
        container_style = self.get_container_style()
        style_str = "; ".join(f"{k}: {v}" for k, v in container_style.items())
        
        card_style = {
            "max-width": "100%",
            "margin": "0 auto",
            "padding": "20px 16px",
            "background-color": self.colors["card_bg"],
            "border-radius": "16px",
            "border": f"1px solid {self.colors['border']}",
            "box-shadow": f"0 4px 20px {self.colors['shadow']}",
        }
        card_style_str = "; ".join(f"{k}: {v}" for k, v in card_style.items())
        
        # 添加顶部装饰
        top_decoration = get_sticker_html("flower", self.colors["tertiary"], 32, "block", "10px auto")
        
        # 添加底部装饰
        bottom_decoration = get_section_divider(self.colors["secondary"])
        
        return f'''<section style="{style_str}">
            {top_decoration}
            <section style="{card_style_str}">
                {html}
            </section>
            {bottom_decoration}
        </section>'''

    def get_sticker_decorations(self) -> Dict[str, str]:
        """获取该主题的贴图装饰配置"""
        return {
            "title_prefix": get_sticker_html("flag", self.colors["primary"], 18),
            "section_icon": get_sticker_html("star", self.colors["tertiary"], 16),
            "tip_icon": get_sticker_html("lightning", self.colors["accent"], 20),
            "important_icon": get_sticker_html("bookmark", self.colors["primary"], 18),
            "quote_icon": get_sticker_html("chat_bubble", self.colors["secondary"], 20),
        }
