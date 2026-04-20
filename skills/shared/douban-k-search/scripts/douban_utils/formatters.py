"""输出格式化。"""

from douban_utils.data_models import (
    Book,
    Comment,
    DetailWithComments,
    Movie,
    Music,
    SearchResponse,
)


def format_search_response(response: SearchResponse) -> str:
    """格式化搜索结果为 Markdown。"""
    lines = [
        f"# 搜索结果: {response.query}",
        "",
        f"类目: {response.category.value}",
        f"共找到 {response.total} 条结果",
        "",
    ]

    for i, item in enumerate(response.results, 1):
        lines.append(f"## {i}. {item.title}")
        lines.append("")
        lines.append(f"- ID: {item.id}")
        if item.rating_value:
            lines.append(f"- 评分: {item.rating_value} ({item.rating_count} 人评价)")
        if item.abstract:
            lines.append(f"- 摘要: {item.abstract}")
        lines.append(f"- 链接: {item.url}")
        lines.append("")

    return "\n".join(lines)


def format_detail(response: DetailWithComments) -> str:
    """格式化详情为 Markdown。"""
    detail = response.detail

    if isinstance(detail, Book):
        return _format_book_detail(detail, response.comments)
    elif isinstance(detail, Movie):
        return _format_movie_detail(detail, response.comments)
    elif isinstance(detail, Music):
        return _format_music_detail(detail, response.comments)

    return ""


def _format_book_detail(book: Book, comments: list[Comment]) -> str:
    """格式化书籍详情。"""
    lines = [
        f"# {book.title}",
        "",
    ]

    if book.subtitle:
        lines.append(f"**副标题**: {book.subtitle}")

    if book.author:
        lines.append(f"**作者**: {' / '.join(book.author)}")

    if book.publisher:
        lines.append(f"**出版社**: {book.publisher}")

    if book.producer:
        lines.append(f"**出品方**: {book.producer}")

    if book.publish_date:
        lines.append(f"**出版年**: {book.publish_date}")

    if book.pages:
        lines.append(f"**页数**: {book.pages}")

    if book.price:
        lines.append(f"**定价**: {book.price}")

    if book.isbn:
        lines.append(f"**ISBN**: {book.isbn}")

    lines.append("")

    if book.rating_value:
        lines.append("## 评分")
        lines.append("")
        lines.append(f"**{book.rating_value}** / 10 ({book.rating_count} 人评价)")
        lines.append("")

    if book.summary:
        lines.append("## 内容简介")
        lines.append("")
        lines.append(book.summary)
        lines.append("")

    if book.author_intro:
        lines.append("## 作者简介")
        lines.append("")
        lines.append(book.author_intro)
        lines.append("")

    if comments:
        lines.extend(_format_comments_section(comments))

    lines.append("---")
    lines.append("")
    lines.append(f"链接: {book.url}")

    return "\n".join(lines)


def _format_movie_detail(movie: Movie, comments: list[Comment]) -> str:
    """格式化电影详情。"""
    lines = [
        f"# {movie.title}",
        "",
    ]

    if movie.original_title:
        lines.append(f"**原名**: {movie.original_title}")

    if movie.director:
        lines.append(f"**导演**: {' / '.join(movie.director)}")

    if movie.writers:
        lines.append(f"**编剧**: {' / '.join(movie.writers)}")

    if movie.actors:
        lines.append(f"**主演**: {' / '.join(movie.actors)}")

    if movie.genres:
        lines.append(f"**类型**: {' / '.join(movie.genres)}")

    if movie.countries:
        lines.append(f"**地区**: {' / '.join(movie.countries)}")

    if movie.release_date:
        lines.append(f"**上映**: {movie.release_date}")

    if movie.runtime:
        lines.append(f"**片长**: {movie.runtime} 分钟")

    lines.append("")

    if movie.rating_value:
        lines.append("## 评分")
        lines.append("")
        lines.append(f"**{movie.rating_value}** / 10 ({movie.rating_count} 人评价)")
        lines.append("")

    if movie.summary:
        lines.append("## 剧情简介")
        lines.append("")
        lines.append(movie.summary)
        lines.append("")

    if comments:
        lines.extend(_format_comments_section(comments))

    lines.append("---")
    lines.append("")
    lines.append(f"链接: {movie.url}")

    return "\n".join(lines)


def _format_music_detail(music: Music, comments: list[Comment]) -> str:
    """格式化音乐详情。"""
    lines = [
        f"# {music.title}",
        "",
    ]

    if music.artist:
        lines.append(f"**表演者**: {music.artist}")

    if music.release_date:
        lines.append(f"**发行时间**: {music.release_date}")

    if music.genres:
        lines.append(f"**流派**: {' / '.join(music.genres)}")

    lines.append("")

    if music.rating_value:
        lines.append("## 评分")
        lines.append("")
        lines.append(f"**{music.rating_value}** / 10 ({music.rating_count} 人评价)")
        lines.append("")

    if comments:
        lines.extend(_format_comments_section(comments))

    lines.append("---")
    lines.append("")
    lines.append(f"链接: {music.url}")

    return "\n".join(lines)


def _format_comments_section(comments: list[Comment]) -> list[str]:
    """格式化短评区块。"""
    lines = [
        f"## 短评 ({len(comments)} 条)",
        "",
    ]

    for c in comments[:10]:
        rating_str = ""
        if c.rating:
            rating_str = f" {'★' * c.rating}{'☆' * (5 - c.rating)}"

        lines.append(f"### {c.user_name}{rating_str}")
        lines.append("")
        lines.append(c.content)
        if c.votes:
            lines.append("")
            lines.append(f"*有用 {c.votes}*")
        lines.append("")

    return lines
