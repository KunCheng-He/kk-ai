"""
知乎工具包。

导出核心模块和类，简化外部导入。
"""

from zhihu_utils.browser import create_browser_context
from zhihu_utils.data_models import (
    SearchResult,
    Answer,
    Question,
    Article,
    SearchResponse,
    SearchType,
)
from zhihu_utils.api_handler import APIHandler
from zhihu_utils.url_parser import parse_url
from zhihu_utils.formatters import html_to_markdown

__all__ = [
    "create_browser_context",
    "SearchResult",
    "Answer",
    "Question",
    "Article",
    "SearchResponse",
    "SearchType",
    "APIHandler",
    "parse_url",
    "html_to_markdown",
]
