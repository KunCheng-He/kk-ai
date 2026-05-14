from typing import Dict

from themes.base import BaseTheme


class MinimalBlueTheme(BaseTheme):
    name = "minimal-blue"
    description = "极简蓝，简洁专业，适合技术文章"

    colors = {
        "background": "#ffffff",
        "text": "#333333",
        "primary": "#1890ff",
        "secondary": "#40a9ff",
        "quote_bg": "#f0f7ff",
        "code_bg": "#f5f5f5",
    }

    typography = {
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        "font_size": "16px",
        "line_height": "1.8",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "25px 20px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "26px", 2: "22px", 3: "20px", 4: "18px", 5: "16px", 6: "14px"}
        return {
            "font-size": sizes.get(level, "16px"),
            "font-weight": "600",
            "color": self.colors["text"],
            "margin": "20px 0 12px",
            "border-left": f"4px solid {self.colors['primary']}" if level <= 2 else "none",
            "padding-left": "12px" if level <= 2 else "0",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 0",
            "text-align": "justify",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 0",
            "padding": "12px 16px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"3px solid {self.colors['primary']}",
            "color": "#555",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "12px 0",
            "padding": "12px",
            "background-color": self.colors["code_bg"],
            "border-radius": "4px",
            "overflow-x": "auto",
            "font-family": "'SF Mono', Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 5px",
            "background-color": self.colors["code_bg"],
            "border-radius": "3px",
            "font-family": "'SF Mono', Consolas, Monaco, 'Courier New', monospace",
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
            "margin": "12px 0",
            "padding-left": "20px",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "5px 0",
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "12px 0",
            "border-collapse": "collapse",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "8px 12px",
            "border": "1px solid #e8e8e8",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "8px 12px",
            "border": "1px solid #e8e8e8",
            "background-color": self.colors["quote_bg"],
            "font-weight": "600",
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "height": "1px",
            "background-color": "#e8e8e8",
            "margin": "20px 0",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "600",
            "color": self.colors["text"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": "#666",
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["primary"],
            "text-decoration": "none",
        }
