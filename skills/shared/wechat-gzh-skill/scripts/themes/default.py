from typing import Dict

from themes.base import BaseTheme


class DefaultTheme(BaseTheme):
    name = "default"
    description = "微信默认风格，简洁通用"

    colors = {
        "background": "#ffffff",
        "text": "#333333",
        "primary": "#07c160",
        "secondary": "#576b95",
        "quote_bg": "#f7f7f7",
        "code_bg": "#f5f5f5",
    }

    typography = {
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        "font_size": "16px",
        "line_height": "1.75",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "20px 15px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "24px", 2: "22px", 3: "20px", 4: "18px", 5: "16px", 6: "14px"}
        margins = {1: "25px 0 15px", 2: "20px 0 12px", 3: "18px 0 10px"}
        return {
            "font-size": sizes.get(level, "16px"),
            "font-weight": "bold",
            "color": self.colors["text"],
            "margin": margins.get(level, "15px 0 8px"),
            "padding-bottom": "8px",
            "border-bottom": "1px solid #eee" if level <= 2 else "none",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "text-align": "justify",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "padding": "10px 15px",
            "background-color": self.colors["quote_bg"],
            "border-left": "4px solid self.colors['primary']",
            "color": "#666",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
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
        }

    def get_image_style(self) -> Dict[str, str]:
        return {
            "max-width": "100%",
            "height": "auto",
            "display": "block",
            "margin": "20px auto",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "padding-left": "25px",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "5px 0",
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "15px 0",
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
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "height": "1px",
            "background-color": "#eee",
            "margin": "20px 0",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["text"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": "#666",
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["secondary"],
            "text-decoration": "none",
        }
