"""数据获取逻辑。"""

from douban_utils.browser import DoubanBrowser
from douban_utils.data_models import (
    Category,
    Comment,
    DetailWithComments,
    SearchResponse,
)
from douban_utils.html_parser import (
    parse_book_detail,
    parse_comments,
    parse_movie_detail,
    parse_music_detail,
)
from douban_utils.http_client import (
    DoubanHttpClient,
    extract_window_data,
    parse_search_results,
)


async def search(query: str, category: Category, limit: int = 10) -> SearchResponse:
    """搜索豆瓣内容。

    Args:
        query: 搜索关键词。
        category: 内容类目。
        limit: 返回数量限制。

    Returns:
        搜索响应。
    """
    client = DoubanHttpClient()
    try:
        html = await client.fetch_search_page(query, category)
        data = extract_window_data(html)

        if not data:
            return SearchResponse(
                query=query,
                category=category,
                results=[],
                total=0,
            )

        results = parse_search_results(data, category)
        total = data.get("total", len(results))

        return SearchResponse(
            query=query,
            category=category,
            results=results[:limit],
            total=total,
        )
    finally:
        await client.close()


async def get_book_detail(
    subject_id: int, with_comments: bool = False
) -> DetailWithComments | None:
    """获取书籍详情。

    Args:
        subject_id: 条目 ID。
        with_comments: 是否获取短评。

    Returns:
        详情+评论，获取失败返回 None。
    """
    client = DoubanHttpClient()
    try:
        html = await client.fetch_detail_page(subject_id, Category.BOOK)
        book = parse_book_detail(html, subject_id)

        if not book:
            return None

        comments: list[Comment] = []
        if with_comments:
            comments_html = await client.fetch_comments_page(subject_id, Category.BOOK)
            comments = parse_comments(comments_html)

        return DetailWithComments(detail=book, comments=comments)
    finally:
        await client.close()


async def get_movie_detail(
    subject_id: int,
    with_comments: bool = False,
    use_cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
) -> DetailWithComments | None:
    """获取电影详情。

    CDP 模式（默认）：连接已有浏览器，处理 POW 验证。
    Launch 模式（use_cdp=False）：启动独立 Chromium。

    Args:
        subject_id: 条目 ID。
        with_comments: 是否获取短评。
        use_cdp: 是否使用 CDP 模式连接已有浏览器。默认 True。
        cdp_url: CDP 调试端点 URL。

    Returns:
        详情+评论，获取失败返回 None。
    """
    return await _get_movie_detail_browser(
        subject_id, with_comments, use_cdp=use_cdp, cdp_url=cdp_url
    )


async def _get_movie_detail_browser(
    subject_id: int,
    with_comments: bool,
    use_cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
) -> DetailWithComments | None:
    """浏览器方式获取电影详情。"""
    browser = DoubanBrowser(use_cdp=use_cdp, cdp_url=cdp_url)
    try:
        await browser.start()
        html = await browser.fetch_movie_detail(subject_id)
        movie = parse_movie_detail(html, subject_id)

        if not movie:
            return None

        comments: list[Comment] = []
        if with_comments:
            comments_html = await browser.fetch_movie_comments(subject_id)
            comments = parse_comments(comments_html)

        return DetailWithComments(detail=movie, comments=comments)
    finally:
        await browser.close()


async def get_music_detail(
    subject_id: int, with_comments: bool = False
) -> DetailWithComments | None:
    """获取音乐详情。

    Args:
        subject_id: 条目 ID。
        with_comments: 是否获取短评。

    Returns:
        详情+评论，获取失败返回 None。
    """
    client = DoubanHttpClient()
    try:
        html = await client.fetch_detail_page(subject_id, Category.MUSIC)
        music = parse_music_detail(html, subject_id)

        if not music:
            return None

        comments: list[Comment] = []
        if with_comments:
            comments_html = await client.fetch_comments_page(subject_id, Category.MUSIC)
            comments = parse_comments(comments_html)

        return DetailWithComments(detail=music, comments=comments)
    finally:
        await client.close()


async def get_detail(
    subject_id: int,
    category: Category,
    with_comments: bool = False,
    use_cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
) -> DetailWithComments | None:
    """获取条目详情（统一入口）。

    Args:
        subject_id: 条目 ID。
        category: 内容类目。
        with_comments: 是否获取短评。
        use_cdp: 是否使用 CDP 模式（仅电影类目用到浏览器）。默认 True。
        cdp_url: CDP 调试端点 URL。

    Returns:
        详情+评论，获取失败返回 None。
    """
    if category == Category.BOOK:
        return await get_book_detail(subject_id, with_comments)
    elif category == Category.MOVIE:
        return await get_movie_detail(subject_id, with_comments, use_cdp=use_cdp, cdp_url=cdp_url)
    elif category == Category.MUSIC:
        return await get_music_detail(subject_id, with_comments)
    return None
