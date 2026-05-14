from typing import Dict

from themes.base import BaseTheme


class ElegantGoldTheme(BaseTheme):
    name = "elegant-gold"
    description = "金色系，层次丰富，左边框递减 + 渐变背景"

    colors = {
        "background": "#faf9f5",
        "text": "#4a413d",
        "primary": "#d97758",
        "secondary": "#c06b4d",
        "quote_bg": "#fef4e7",
        "code_bg": "#f5f2ed",
        "card_bg": "#ffffff",
    }

    typography = {
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        "font_size": "16px",
        "line_height": "1.75",
        "letter_spacing": "0.5px",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "40px 10px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
            "letter-spacing": self.typography["letter_spacing"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "24px", 2: "22px", 3: "20px", 4: "18px", 5: "16px", 6: "14px"}
        borders = {1: "5px", 2: "4px", 3: "3px", 4: "2px", 5: "1px", 6: "1px"}
        return {
            "font-size": sizes.get(level, "16px"),
            "font-weight": "bold",
            "color": self.colors["primary"],
            "margin": "25px 0 15px",
            "padding-left": borders.get(level, "1px"),
            "border-left": f"{borders.get(level, '1px')} solid {self.colors['primary']}",
        }

    def get_paragraph_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "text-align": "justify",
            "color": self.colors["text"],
        }

    def get_blockquote_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "padding": "15px 20px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"5px solid {self.colors['primary']}",
            "box-shadow": "inset 0 0 15px rgba(217, 119, 88, 0.1)",
            "color": self.colors["text"],
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "padding": "15px",
            "background-color": self.colors["code_bg"],
            "border-radius": "8px",
            "overflow-x": "auto",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "border": f"1px solid rgba(217, 119, 88, 0.2)",
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
            "margin": "20px auto",
            "border-radius": "8px",
            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 0",
            "padding-left": "25px",
        }

    def get_list_item_style(self) -> Dict[str, str]:
        return {
            "margin": "8px 0",
            "color": self.colors["text"],
        }

    def get_table_style(self) -> Dict[str, str]:
        return {
            "width": "100%",
            "margin": "15px 0",
            "border-collapse": "collapse",
            "border-radius": "8px",
            "overflow": "hidden",
        }

    def get_table_cell_style(self) -> Dict[str, str]:
        return {
            "padding": "12px",
            "border": f"1px solid rgba(217, 119, 88, 0.2)",
        }

    def get_table_header_style(self) -> Dict[str, str]:
        return {
            "padding": "12px",
            "border": f"1px solid rgba(217, 119, 88, 0.2)",
            "background-color": self.colors["quote_bg"],
            "font-weight": "bold",
            "color": self.colors["primary"],
        }

    def get_hr_style(self) -> Dict[str, str]:
        return {
            "border": "none",
            "height": "1px",
            "background-color": "rgba(74, 65, 61, 0.1)",
            "margin": "25px 0",
        }

    def get_strong_style(self) -> Dict[str, str]:
        return {
            "font-weight": "bold",
            "color": self.colors["secondary"],
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
        }

    def wrap_content(self, html: str) -> str:
        container_style = self.get_container_style()
        style_str = "; ".join(f"{k}: {v}" for k, v in container_style.items())
        card_style = {
            "max-width": "800px",
            "margin": "0 auto",
            "padding": "25px",
            "background-color": self.colors["card_bg"],
            "border-radius": "18px",
            "border": "1px solid rgba(0, 0, 0, 0.05)",
            "box-shadow": "0 10px 30px rgba(0, 0, 0, 0.04), 0 0 15px rgba(217, 119, 88, 0.4)",
        }
        card_style_str = "; ".join(f"{k}: {v}" for k, v in card_style.items())
        return f'<section style="{style_str}"><section style="{card_style_str}">{html}</section></section>'