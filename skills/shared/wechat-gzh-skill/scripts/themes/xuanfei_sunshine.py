from typing import Dict

from themes.base import BaseTheme


class XuanfeiSunshineTheme(BaseTheme):
    name = "xuanfei-sunshine"
    description = "轩飞阳光，金黄标题 + 蓝色点缀，活泼温暖，适合运营分享、生活随笔"

    colors = {
        "background": "#ffffff",
        "text": "#565656",
        "primary": "#ffc800",
        "secondary": "#78b5e3",
        "heading_text": "#ffffff",
        "subtitle": "#888888",
        "quote_bg": "#fffcf0",
        "code_bg": "#f8f8f8",
        "divider": "rgba(0,0,0,0.1)",
    }

    typography = {
        "font_family": "system-ui, -apple-system, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif",
        "font_size": "16px",
        "line_height": "1.75",
        "letter_spacing": "0.5px",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "20px 16px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
            "letter-spacing": self.typography["letter_spacing"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "24px", 2: "22px", 3: "20px", 4: "18px", 5: "16px", 6: "14px"}
        if level <= 2:
            return {
                "font-size": sizes.get(level, "24px"),
                "font-weight": "700",
                "color": self.colors["heading_text"],
                "background-color": self.colors["primary"],
                "display": "inline-block",
                "padding": "4px 12px",
                "margin": "25px 0 15px",
                "line-height": "28px",
                "letter-spacing": "0.5px",
            }
        return {
            "font-size": sizes.get(level, "16px"),
            "font-weight": "bold",
            "color": self.colors["text"],
            "margin": "18px 0 10px",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 16px",
            "text-align": "justify",
            "color": self.colors["text"],
            "line-height": "25.6px",
            "letter-spacing": "0.5px",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 16px",
            "padding": "12px 18px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"4px solid {self.colors['primary']}",
            "color": self.colors["subtitle"],
            "font-size": "14px",
            "line-height": "1.75em",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 16px",
            "padding": "15px",
            "background-color": self.colors["code_bg"],
            "border-radius": "4px",
            "overflow-x": "auto",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 6px",
            "background-color": self.colors["code_bg"],
            "border-radius": "3px",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "color": self.colors["secondary"],
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
            "margin": "12px 16px",
            "padding-left": "25px",
            "line-height": "1.75em",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "6px 0",
            "color": self.colors["text"],
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "15px 16px",
            "border-collapse": "collapse",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "10px",
            "border": "1px solid #eee",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "10px",
            "border": "1px solid #eee",
            "background-color": self.colors["quote_bg"],
            "font-weight": "bold",
            "color": self.colors["text"],
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "border-top": "1px solid " + self.colors["divider"],
            "margin": "20px 16px",
            "transform-origin": "0 0",
            "transform": "scale(1, 0.5)",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["text"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": self.colors["secondary"],
            "text-decoration": "underline",
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["secondary"],
            "text-decoration": "none",
            "font-weight": "bold",
        }
