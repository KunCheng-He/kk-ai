"""
数据模型定义模块。

定义知乎搜索、问题、回答、文章等核心数据结构。
所有模型使用 Pydantic 实现，支持数据验证和序列化。
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """搜索类型枚举。"""

    ALL = "all"
    QUESTION = "question"
    ANSWER = "answer"
    ARTICLE = "article"
    USER = "people"


class SearchResult(BaseModel):
    """搜索结果模型。"""

    id: str
    type: str = Field(description="内容类型: answer, article, question, people")
    title: str
    excerpt: str = Field(default="", description="内容摘要")
    author: str | None = None
    url: str
    vote_count: int = 0
    comment_count: int = 0
    created_at: datetime | None = None


class Answer(BaseModel):
    """回答模型。"""

    id: int
    question_id: int
    question_title: str = ""
    content: str
    excerpt: str = ""
    author_name: str
    author_url_token: str | None = None
    vote_count: int = 0
    comment_count: int = 0
    created_at: datetime | None = None
    url: str = ""


class Question(BaseModel):
    """问题模型。"""

    id: int
    title: str
    detail: str = ""
    answer_count: int = 0
    follower_count: int = 0
    created_at: datetime | None = None
    url: str = ""


class Article(BaseModel):
    """文章模型。"""

    id: str
    title: str
    content: str = ""
    excerpt: str = ""
    author_name: str
    author_url_token: str | None = None
    vote_count: int = 0
    comment_count: int = 0
    created_at: datetime | None = None
    url: str = ""


class SearchResponse(BaseModel):
    """搜索响应模型，包含分页信息。"""

    query: str
    results: list[SearchResult] = []
    total: int = 0
    has_more: bool = False
    next_offset: int | None = None
