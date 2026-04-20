"""Pydantic 数据模型定义。"""

from enum import Enum

from pydantic import BaseModel


class Category(str, Enum):
    """内容类目。"""

    BOOK = "book"
    MOVIE = "movie"
    MUSIC = "music"


class SearchResult(BaseModel):
    """搜索结果。"""

    id: int
    category: Category
    title: str
    url: str
    cover_url: str | None = None
    rating_value: float | None = None
    rating_count: int = 0
    abstract: str = ""


class Rating(BaseModel):
    """评分分布。"""

    stars_5: float = 0
    stars_4: float = 0
    stars_3: float = 0
    stars_2: float = 0
    stars_1: float = 0


class Book(BaseModel):
    """书籍详情。"""

    id: int
    title: str
    subtitle: str | None = None
    author: list[str] = []
    publisher: str | None = None
    producer: str | None = None
    publish_date: str | None = None
    isbn: str | None = None
    pages: int | None = None
    price: str | None = None
    binding: str | None = None
    series: str | None = None
    rating_value: float | None = None
    rating_count: int = 0
    rating_distribution: Rating | None = None
    summary: str = ""
    author_intro: str = ""
    url: str


class Movie(BaseModel):
    """电影详情。"""

    id: int
    title: str
    original_title: str | None = None
    director: list[str] = []
    writers: list[str] = []
    actors: list[str] = []
    genres: list[str] = []
    countries: list[str] = []
    languages: list[str] = []
    release_date: str | None = None
    runtime: int | None = None
    rating_value: float | None = None
    rating_count: int = 0
    rating_distribution: Rating | None = None
    summary: str = ""
    url: str


class Music(BaseModel):
    """音乐详情。"""

    id: int
    title: str
    artist: str | None = None
    release_date: str | None = None
    genres: list[str] = []
    rating_value: float | None = None
    rating_count: int = 0
    rating_distribution: Rating | None = None
    url: str


class Comment(BaseModel):
    """短评。"""

    id: str
    user_name: str
    user_url: str | None = None
    rating: int | None = None
    content: str
    votes: int = 0
    created_at: str | None = None


class SearchResponse(BaseModel):
    """搜索响应。"""

    query: str
    category: Category
    results: list[SearchResult] = []
    total: int = 0


class DetailWithComments(BaseModel):
    """详情+评论。"""

    detail: Book | Movie | Music
    comments: list[Comment] = []
