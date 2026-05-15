from typing import Dict, Optional, Type

from themes.base import BaseTheme
from themes.default import DefaultTheme
from themes.elegant_gold import ElegantGoldTheme
from themes.autumn_warm import AutumnWarmTheme
from themes.minimal_blue import MinimalBlueTheme
from themes.spring_fresh import SpringFreshTheme
from themes.wenxin_crimson import WenxinCrimsonTheme
from themes.xuanfei_sunshine import XuanfeiSunshineTheme
from themes.juanran_pastel import JuanranPastelTheme
from themes.xiumi_style import XiumiStyleTheme


_THEMES: Dict[str, Type[BaseTheme]] = {
    "default": DefaultTheme,
    "elegant-gold": ElegantGoldTheme,
    "autumn-warm": AutumnWarmTheme,
    "minimal-blue": MinimalBlueTheme,
    "spring-fresh": SpringFreshTheme,
    "wenxin-crimson": WenxinCrimsonTheme,
    "xuanfei-sunshine": XuanfeiSunshineTheme,
    "juanran-pastel": JuanranPastelTheme,
    "xiumi-style": XiumiStyleTheme,
}


def get_theme(name: str) -> BaseTheme:
    if name not in _THEMES:
        available = ", ".join(_THEMES.keys())
        raise ValueError(f"未知主题: {name}，可用主题: {available}")
    return _THEMES[name]()


def list_themes() -> Dict[str, str]:
    return {name: cls().description for name, cls in _THEMES.items()}
