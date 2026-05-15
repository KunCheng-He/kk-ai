"""
SVG 贴图素材库
包含各种装饰性 SVG 贴图，可直接嵌入 HTML 使用
"""

from typing import Dict, List

# 贴图定义
STICKERS: Dict[str, Dict] = {
    # ========== 装饰性元素 ==========
    "star": {
        "name": "星星",
        "category": "decoration",
        "svg": '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L14.09 8.26L21 9.27L16.5 14.14L17.82 21.02L12 17.77L6.18 21.02L7.5 14.14L3 9.27L9.91 8.26L12 2Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#FFD700"
    },
    
    "heart": {
        "name": "爱心",
        "category": "decoration",
        "svg": '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="currentColor"/>
        </svg>''',
        "default_color": "#FF6B6B"
    },
    
    "sparkle": {
        "name": "闪光",
        "category": "decoration",
        "svg": '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L13.5 9H12V2ZM12 22V15H13.5L12 22ZM2 12L9 13.5V12H2ZM22 12H15V13.5L22 12Z" fill="currentColor"/>
            <circle cx="12" cy="12" r="3" fill="currentColor"/>
        </svg>''',
        "default_color": "#FFD93D"
    },
    
    "flower": {
        "name": "花朵",
        "category": "decoration",
        "svg": '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="4" fill="currentColor"/>
            <ellipse cx="16" cy="6" rx="4" ry="6" fill="currentColor" opacity="0.8"/>
            <ellipse cx="16" cy="26" rx="4" ry="6" fill="currentColor" opacity="0.8"/>
            <ellipse cx="6" cy="16" rx="6" ry="4" fill="currentColor" opacity="0.8"/>
            <ellipse cx="26" cy="16" rx="6" ry="4" fill="currentColor" opacity="0.8"/>
        </svg>''',
        "default_color": "#FF9A9E"
    },
    
    "leaf": {
        "name": "叶子",
        "category": "decoration",
        "svg": '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2C14 2 24 8 24 16C24 22 19 26 14 26C9 26 4 22 4 16C4 8 14 2 14 2Z" fill="currentColor"/>
            <path d="M14 26V10" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        "default_color": "#7BC4A0"
    },
    
    # ========== 箭头 ==========
    "arrow_right": {
        "name": "右箭头",
        "category": "arrow",
        "svg": '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4L10.59 5.41L16.17 11H4V13H16.17L10.59 18.59L12 20L20 12L12 4Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#666666"
    },
    
    "arrow_down": {
        "name": "下箭头",
        "category": "arrow",
        "svg": '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 12L18.59 10.59L13 16.17V4H11V16.17L5.41 10.59L4 12L12 20L20 12Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#666666"
    },
    
    "arrow_curved": {
        "name": "弯曲箭头",
        "category": "arrow",
        "svg": '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 8C8 8 8 20 20 20L24 20L20 16M20 24L24 20" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        "default_color": "#FF6B6B"
    },
    
    # ========== 标签/标记 ==========
    "tag": {
        "name": "标签",
        "category": "label",
        "svg": '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4L4 12L14 24L24 14L12 4H4Z" fill="currentColor"/>
            <circle cx="8" cy="8" r="2" fill="white"/>
        </svg>''',
        "default_color": "#E8836B"
    },
    
    "bookmark": {
        "name": "书签",
        "category": "label",
        "svg": '''<svg width="24" height="28" viewBox="0 0 24 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 2H20V26L12 20L4 26V2Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#F0C96E"
    },
    
    "flag": {
        "name": "旗帜",
        "category": "label",
        "svg": '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 4V24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M6 6H22L18 12L22 18H6" fill="currentColor"/>
        </svg>''',
        "default_color": "#7BC4A0"
    },
    
    # ========== 几何图形 ==========
    "circle_ring": {
        "name": "圆环",
        "category": "shape",
        "svg": '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="12" stroke="currentColor" stroke-width="3" fill="none"/>
            <circle cx="16" cy="16" r="6" fill="currentColor"/>
        </svg>''',
        "default_color": "#9B59B6"
    },
    
    "diamond": {
        "name": "菱形",
        "category": "shape",
        "svg": '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="14" y="2" width="16" height="16" transform="rotate(45 14 14)" fill="currentColor"/>
        </svg>''',
        "default_color": "#3498DB"
    },
    
    "hexagon": {
        "name": "六边形",
        "category": "shape",
        "svg": '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 2L28 9V23L16 30L4 23V9L16 2Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#E74C3C"
    },
    
    # ========== 特殊装饰 ==========
    "ribbon": {
        "name": "丝带",
        "category": "special",
        "svg": '''<svg width="40" height="32" viewBox="0 0 40 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 4L24 12H16L20 4Z" fill="currentColor"/>
            <path d="M8 12L20 12L16 28L8 12Z" fill="currentColor" opacity="0.8"/>
            <path d="M32 12L20 12L24 28L32 12Z" fill="currentColor" opacity="0.8"/>
        </svg>''',
        "default_color": "#E8836B"
    },
    
    "crown": {
        "name": "皇冠",
        "category": "special",
        "svg": '''<svg width="32" height="28" viewBox="0 0 32 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 20L8 8L16 16L24 8L28 20H4Z" fill="currentColor"/>
            <circle cx="8" cy="6" r="2" fill="currentColor"/>
            <circle cx="16" cy="6" r="2" fill="currentColor"/>
            <circle cx="24" cy="6" r="2" fill="currentColor"/>
            <rect x="4" y="20" width="24" height="4" fill="currentColor" opacity="0.6"/>
        </svg>''',
        "default_color": "#FFD700"
    },
    
    "lightning": {
        "name": "闪电",
        "category": "special",
        "svg": '''<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 16H11L9 30L19 14H11L13 2Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#FFD93D"
    },
    
    "chat_bubble": {
        "name": "对话气泡",
        "category": "special",
        "svg": '''<svg width="32" height="28" viewBox="0 0 32 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4H28V20H18L12 26V20H4V4Z" fill="currentColor"/>
        </svg>''',
        "default_color": "#3498DB"
    },
    
    "music_note": {
        "name": "音符",
        "category": "special",
        "svg": '''<svg width="28" height="32" viewBox="0 0 28 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 26C10 28.2091 8.20914 30 6 30C3.79086 30 2 28.2091 2 26C2 23.7909 3.79086 22 6 22C8.20914 22 10 23.7909 10 26Z" fill="currentColor"/>
            <path d="M26 22C26 24.2091 24.2091 26 22 26C19.7909 26 18 24.2091 18 22C18 19.7909 19.7909 18 22 18C24.2091 18 26 19.7909 26 22Z" fill="currentColor"/>
            <path d="M10 26V6L26 2V22" stroke="currentColor" stroke-width="3" fill="none"/>
        </svg>''',
        "default_color": "#9B59B6"
    },
    
    "gift": {
        "name": "礼物",
        "category": "special",
        "svg": '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="10" width="20" height="14" fill="currentColor"/>
            <rect x="12" y="10" width="4" height="14" fill="white" opacity="0.3"/>
            <path d="M14 10C14 10 18 6 18 4C18 2 16 2 14 4C12 2 10 2 10 4C10 6 14 10 14 10Z" fill="currentColor" opacity="0.7"/>
        </svg>''',
        "default_color": "#E74C3C"
    },
}


def get_sticker(sticker_id: str, color: str = None, size: int = 24) -> Dict:
    """
    获取贴图定义
    
    Args:
        sticker_id: 贴图ID
        color: 自定义颜色（可选）
        size: 尺寸（可选）
    
    Returns:
        贴图定义字典
    """
    if sticker_id not in STICKERS:
        return None
    
    sticker = STICKERS[sticker_id].copy()
    if color:
        sticker["default_color"] = color
    sticker["size"] = size
    return sticker


def get_sticker_html(sticker_id: str, color: str = None, size: int = 24, 
                     position: str = "inline", margin: str = "0 4px") -> str:
    """
    获取贴图的 HTML 代码
    
    Args:
        sticker_id: 贴图ID
        color: 自定义颜色
        size: 尺寸
        position: 定位方式 (inline, block, absolute)
        margin: 外边距
    
    Returns:
        HTML 字符串
    """
    sticker = get_sticker(sticker_id, color, size)
    if not sticker:
        return ""
    
    svg_content = sticker["svg"]
    sticker_color = sticker.get("default_color", "#666666")
    
    # 替换颜色
    svg_content = svg_content.replace('fill="currentColor"', f'fill="{sticker_color}"')
    svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{sticker_color}"')
    
    # 设置尺寸
    svg_content = svg_content.replace('width="24"', f'width="{size}"')
    svg_content = svg_content.replace('width="28"', f'width="{size}"')
    svg_content = svg_content.replace('width="32"', f'width="{size}"')
    svg_content = svg_content.replace('width="40"', f'width="{size}"')
    svg_content = svg_content.replace('height="24"', f'height="{size}"')
    svg_content = svg_content.replace('height="28"', f'height="{size}"')
    svg_content = svg_content.replace('height="32"', f'height="{size}"')
    
    # 移除所有换行和多余空格，避免 Markdown 转换器插入 <br/>
    svg_content = ' '.join(svg_content.split())
    
    if position == "block":
        return f'<div style="text-align: center; margin: {margin};">{svg_content}</div>'
    elif position == "absolute":
        return f'<span style="position: absolute; display: inline-block; margin: {margin};">{svg_content}</span>'
    else:
        return f'<span style="display: inline-block; vertical-align: middle; margin: {margin};">{svg_content}</span>'


def list_stickers(category: str = None) -> List[Dict]:
    """
    列出所有贴图
    
    Args:
        category: 分类过滤（可选）
    
    Returns:
        贴图列表
    """
    result = []
    for sticker_id, sticker in STICKERS.items():
        if category and sticker.get("category") != category:
            continue
        result.append({
            "id": sticker_id,
            "name": sticker["name"],
            "category": sticker.get("category", "other"),
            "default_color": sticker.get("default_color", "#666666")
        })
    return result


# 快捷函数：常用贴图组合
def get_title_decorations(color: str = "#E8836B") -> Dict[str, str]:
    """获取标题装饰贴图组合"""
    return {
        "left": get_sticker_html("star", color, 20),
        "right": get_sticker_html("sparkle", color, 18),
        "prefix": get_sticker_html("flag", color, 16),
    }


def get_section_divider(color: str = "#7BC4A0") -> str:
    """获取章节分隔线装饰"""
    leaf_left = get_sticker_html("leaf", color, 20)
    leaf_right = get_sticker_html("leaf", color, 20)
    return f'<div style="text-align: center; margin: 20px 0; opacity: 0.6;">{leaf_left}<span style="margin: 0 10px; color: {color}; font-size: 14px;">✦ ✦ ✦</span>{leaf_right}</div>'


def get_tip_box_icon(color: str = "#FFD93D") -> str:
    """获取提示框图标"""
    return get_sticker_html("lightning", color, 24)


def get_important_mark(color: str = "#E74C3C") -> str:
    """获取重要标记"""
    return get_sticker_html("bookmark", color, 20)
