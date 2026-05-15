from typing import Dict

from themes.base import BaseTheme


class JuanranPastelTheme(BaseTheme):
    name = "juanran-pastel"
    description = "娟然粉彩，柔和暖色卡片 + 圆角贴图感，适合新手教程、轻松分享"

    colors = {
        "background": "#fff7f5",
        "card_bg": "#ffffff",
        "text": "#4a4a4a",
        "primary": "#e8836b",
        "secondary": "#7bc4a0",
        "tertiary": "#f0c96e",
        "subtitle": "#999999",
        "quote_bg": "#fff0ed",
        "code_bg": "#fdf5f3",
        "border": "rgba(232, 131, 107, 0.2)",
        "shadow": "rgba(232, 131, 107, 0.08)",
    }

    typography = {
        "font_family": "'PingFang SC', system-ui, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif",
        "font_size": "15px",
        "line_height": "2",
        "letter_spacing": "0.5px",
    }

    def get_container_style(self) -> Dict[str, str]:
        return {
            "padding": "30px 12px",
            "background-color": self.colors["background"],
            "color": self.colors["text"],
            "font-family": self.typography["font_family"],
            "font-size": self.typography["font_size"],
            "line-height": self.typography["line_height"],
            "letter-spacing": self.typography["letter_spacing"],
        }

    def get_heading_style(self, level: int) -> Dict[str, str]:
        sizes = {1: "20px", 2: "18px", 3: "17px", 4: "16px", 5: "15px", 6: "14px"}
        bg_colors = {
            1: self.colors["primary"],
            2: self.colors["secondary"],
            3: self.colors["tertiary"],
        }
        if level <= 3:
            return {
                "font-size": sizes.get(level, "16px"),
                "font-weight": "bold",
                "color": "#ffffff",
                "background-color": bg_colors.get(level, self.colors["primary"]),
                "display": "inline-block",
                "padding": "6px 16px",
                "border-radius": "20px",
                "margin": "22px 0 12px",
                "line-height": "1.6",
                "letter-spacing": "1px",
            }
        return {
            "font-size": sizes.get(level, "15px"),
            "font-weight": "bold",
            "color": self.colors["primary"],
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
            "padding": "14px 18px",
            "background-color": self.colors["quote_bg"],
            "border-left": f"4px solid {self.colors['primary']}",
            "border-radius": "0 12px 12px 0",
            "color": self.colors["subtitle"],
            "font-size": "14px",
            "line-height": "1.8em",
        }

    def get_code_block_style(self) -> Dict[str, str]:
        return {
            "margin": "15px 8px",
            "padding": "15px",
            "background-color": self.colors["code_bg"],
            "border-radius": "12px",
            "overflow-x": "auto",
            "font-family": "Consolas, Monaco, 'Courier New', monospace",
            "font-size": "14px",
            "border": f"1px solid {self.colors['border']}",
        }

    def get_inline_code_style(self) -> Dict[str, str]:
        return {
            "padding": "2px 8px",
            "background-color": self.colors["quote_bg"],
            "border-radius": "10px",
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
            "border-radius": "12px",
            "box-shadow": f"0 4px 12px {self.colors['shadow']}",
        }

    def get_list_style(self) -> Dict[str, str]:
        return {
            "margin": "10px 8px",
            "padding-left": "25px",
            "line-height": "2em",
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
            "border-collapse": "collapse",
            "border-radius": "12px",
            "overflow": "hidden",
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
            "height": "2px",
            "background": f"linear-gradient(to right, {self.colors['primary']}, {self.colors['secondary']}, {self.colors['tertiary']})",
            "margin": "25px 8px",
            "border-radius": "1px",
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
            "color": self.colors["primary"],
            "text-decoration": "none",
            "border-bottom": f"1px dashed {self.colors['secondary']}",
        }

    def wrap_content(self, html: str) -> str:
        container_style = self.get_container_style()
        style_str = "; ".join(f"{k}: {v}" for k, v in container_style.items())
        card_style = {
            "max-width": "100%",
            "margin": "0 auto",
            "padding": "20px 16px",
            "background-color": self.colors["card_bg"],
            "border-radius": "16px",
            "border": f"1px solid {self.colors['border']}",
            "box-shadow": f"0 6px 20px {self.colors['shadow']}",
        }
        card_style_str = "; ".join(f"{k}: {v}" for k, v in card_style.items())
        return f'<section style="{style_str}"><section style="{card_style_str}">{html}</section></section>'
