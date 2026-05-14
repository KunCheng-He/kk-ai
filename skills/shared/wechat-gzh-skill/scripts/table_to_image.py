import os
import tempfile
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from bs4 import BeautifulSoup, Tag


plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "STHeiti", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def extract_table_data(table: Tag) -> Tuple[List[str], List[List[str]]]:
    headers = []
    rows = []
    
    header_row = table.find("tr")
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            headers.append(th.get_text(strip=True))
    
    for tr in table.find_all("tr")[1:]:
        row = []
        for td in tr.find_all("td"):
            text = td.get_text(strip=True)
            if not text:
                text = ""
            row.append(text)
        if row:
            rows.append(row)
    
    if not headers and rows:
        headers = rows[0]
        rows = rows[1:]
    
    return headers, rows


def render_table_to_image(
    headers: List[str],
    rows: List[List[str]],
    theme_colors: dict,
    max_width: int = 750,
    output_path: str = None,
) -> str:
    if not output_path:
        output_path = tempfile.mktemp(suffix=".png", prefix="table_")
    
    col_count = max(len(headers), max(len(row) for row in rows) if rows else 0)
    row_count = len(rows) + 1
    
    cell_width = max_width / col_count
    cell_height = 40
    
    fig_width = max_width / 100
    fig_height = (row_count * cell_height + 20) / 100
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, max_width)
    ax.set_ylim(0, row_count * cell_height + 20)
    ax.axis("off")
    
    bg_color = theme_colors.get("background", "#ffffff")
    fig.patch.set_facecolor(bg_color)
    
    header_bg = theme_colors.get("table_header_bg", "#f0f0f0")
    header_text_color = theme_colors.get("table_header_text", "#333333")
    cell_bg = theme_colors.get("table_cell_bg", "#ffffff")
    cell_text_color = theme_colors.get("table_cell_text", "#333333")
    border_color = theme_colors.get("table_border", "#e0e0e0")
    
    for col_idx, header in enumerate(headers):
        x = col_idx * cell_width
        y = row_count * cell_height - cell_height
        
        rect = patches.FancyBboxPatch(
            (x, y), cell_width, cell_height,
            boxstyle="square",
            facecolor=header_bg,
            edgecolor=border_color,
            linewidth=1,
        )
        ax.add_patch(rect)
        
        ax.text(
            x + cell_width / 2, y + cell_height / 2,
            header,
            ha="center", va="center",
            fontsize=12, fontweight="bold",
            color=header_text_color,
        )
    
    for row_idx, row in enumerate(rows):
        for col_idx, cell_text in enumerate(row):
            x = col_idx * cell_width
            y = (row_count - row_idx - 2) * cell_height
            
            rect = patches.FancyBboxPatch(
                (x, y), cell_width, cell_height,
                boxstyle="square",
                facecolor=cell_bg,
                edgecolor=border_color,
                linewidth=1,
            )
            ax.add_patch(rect)
            
            display_text = cell_text[:20] + "..." if len(cell_text) > 20 else cell_text
            
            ax.text(
                x + cell_width / 2, y + cell_height / 2,
                display_text,
                ha="center", va="center",
                fontsize=11,
                color=cell_text_color,
            )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=bg_color)
    plt.close()
    
    return output_path


def table_to_image(table: Tag, theme_colors: dict) -> str:
    headers, rows = extract_table_data(table)
    
    if not headers and not rows:
        return None
    
    return render_table_to_image(headers, rows, theme_colors)


def convert_tables_to_images(soup: BeautifulSoup, theme_colors: dict) -> List[str]:
    image_paths = []
    
    tables = soup.find_all("table")
    
    for idx, table in enumerate(tables):
        image_path = table_to_image(table, theme_colors)
        
        if image_path:
            image_paths.append(image_path)
            
            img_tag = soup.new_tag("img")
            img_tag["src"] = f"TABLE_IMG_PLACEHOLDER_{idx}"
            img_tag["style"] = "max-width:100%;height:auto;display:block;margin:15px auto;"
            
            table.replace_with(img_tag)
    
    return image_paths