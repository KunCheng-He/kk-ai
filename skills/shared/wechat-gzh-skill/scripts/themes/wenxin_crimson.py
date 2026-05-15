from typing import Dict

from themes.base import BaseTheme


class WenxinCrimsonTheme(BaseTheme):
    name = "wenxin-crimson"
    description = "温心深红，简洁克制，品牌色高亮标题 + 深灰正文，适合写作笔记、深度分享"

    colors = {
        "background": "#ffffff",
        "text": "#3e3e3e",
        "primary": "#7b0c00",
        "secondary": "#5f9cef",
        "subtitle": "#888888",
        "quote_bg": "#fef5f4",
        "code_bg": "#f8f5f5",
        "accent_light": "#c2daf1",
        "divider": "#3a528f",
    }

    typography = {
        "font_family": "'PingFang SC', system-ui, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif",
        "font_size": "16px",
        "line_height": "2",
        "letter_spacing": "0.5px",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "20px 8px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
            "letter-spacing": self.typography["letter_spacing"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "16px", 2: "16px", 3: "16px", 4: "15px", 5: "14px", 6: "14px"}
        if level <= 2:
            return {
                "font-size": sizes.get(level, "16px"),
                "font-weight": "bold",
                "color": "#ffffff",
                "background-color": self.colors["primary"],
                "display": "inline-block",
                "padding": "2px 8px",
                "margin": "20px 0 12px",
                "line-height": "1.8",
            }
        return {
            "font-size": sizes.get(level, "16px"),
            "font-weight": "bold",
            "color": self.colors["text"],
            "margin": "15px 0 8px",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "10px 8px",
            "text-align": "justify",
            "color": self.colors["text"],
            "line-height": "2em",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 8px",
            "padding": "12px 16px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"4px solid {self.colors['primary']}",
            "color": self.colors["subtitle"],
            "font-size": "14px",
            "line-height": "1.8em",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 8px",
            "padding": "15px",
            "background-color": self.colors["code_bg"],
            "border-radius": "4px",
            "overflow-x": "auto",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "border": f"1px solid rgba(123, 12, 0, 0.1)",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 6px",
            "background-color": self.colors["code_bg"],
            "border-radius": "3px",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "color": self.colors["primary"],
        }

    def get_image_style(self) -> Dict[str, str]:
        return {
            "max-width": "100%",
            "height": "auto",
            "display": "block",
            "margin": "15px auto",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "10px 8px",
            "padding-left": "25px",
            "line-height": "2em",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "5px 0",
            "color": self.colors["text"],
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "15px 8px",
            "border-collapse": "collapse",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "10px",
            "border": f"1px solid rgba(123, 12, 0, 0.15)",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "10px",
            "border": f"1px solid rgba(123, 12, 0, 0.15)",
            "background-color": self.colors["quote_bg"],
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "border-top": "1px dashed " + self.colors["divider"],
            "margin": "20px 8px",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": self.colors["subtitle"],
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["secondary"],
            "text-decoration": "none",
        }
