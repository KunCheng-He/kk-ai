from typing import Dict

from themes.base import BaseTheme


class SpringFreshTheme(BaseTheme):
    name = "spring-fresh"
    description = "春日清新，绿色调，适合科技、教程类文章"

    colors = {
        "background": "#fafffe",
        "text": "#2c3e50",
        "primary": "#27ae60",
        "secondary": "#2ecc71",
        "quote_bg": "#e8f8f0",
        "code_bg": "#f5f9f7",
    }

    typography = {
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif",
        "font_size": "16px",
        "line_height": "1.75",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "30px 20px",
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
            "font-weight": "bold",
            "color": self.colors["primary"],
            "margin": "22px 0 14px",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "14px 0",
            "text-align": "justify",
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "14px 0",
            "padding": "12px 18px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"4px solid {self.colors['primary']}",
            "border-radius": "0 8px 8px 0",
            "color": "#34495e",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "14px 0",
            "padding": "14px",
            "background-color": self.colors["code_bg"],
            "border-radius": "6px",
            "overflow-x": "auto",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "border": f"1px solid {self.colors['secondary']}",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 6px",
            "background-color": self.colors["quote_bg"],
            "border-radius": "4px",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "color": self.colors["primary"],
        }

    def get_image_style(self) -> Dict[str, str]:
        return {
            "max-width": "100%",
            "height": "auto",
            "display": "block",
            "margin": "18px auto",
            "border-radius": "8px",
            "box-shadow": "0 2px 8px rgba(39, 174, 96, 0.15)",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "14px 0",
            "padding-left": "22px",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "6px 0",
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "14px 0",
            "border-collapse": "collapse",
            "border-radius": "6px",
            "overflow": "hidden",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "10px 14px",
            "border": f"1px solid {self.colors['secondary']}",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "10px 14px",
            "border": f"1px solid {self.colors['secondary']}",
            "background-color": self.colors["quote_bg"],
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "height": "2px",
            "background": f"linear-gradient(to right, transparent, {self.colors['secondary']}, transparent)",
            "margin": "25px 0",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_em_style(self) -> Dict[str, str]:
        return {
            "font-style": "italic",
            "color": self.colors["primary"],
        }

    def get_link_style(self) -> Dict[str, str]:
        return {
            "color": self.colors["primary"],
            "text-decoration": "none",
            "border-bottom": f"1px dashed {self.colors['secondary']}",
        }
