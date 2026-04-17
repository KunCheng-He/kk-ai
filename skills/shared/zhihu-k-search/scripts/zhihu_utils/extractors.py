"""
DOM 提取器模块。

当 API 拦截失败时，通过解析页面 DOM 结构提取数据。
作为数据获取的备用方案。
"""

from playwright.async_api import Page
from zhihu_utils.data_models import SearchResult


async def extract_search_results(page: Page) -> list[SearchResult]:
    """
    从搜索结果页面提取搜索结果列表。

    Args:
        page: Playwright 页面对象。

    Returns:
        SearchResult 对象列表。
    """
    results: list[SearchResult] = []

    await page.wait_for_selector(".SearchResult-Card, .List-item", timeout=10000)

    cards = await page.locator(".SearchResult-Card, .List-item").all()

    for card in cards:
        result = await _extract_search_card(card)
        if result:
            results.append(result)

    return results


async def _extract_search_card(card) -> SearchResult | None:
    """
    从单个搜索卡片元素提取数据。

    Args:
        card: 卡片元素定位器。

    Returns:
        SearchResult 对象或 None。
    """
    try:
        title_el = card.locator("h2 a, .ContentItem-title a")
        if await title_el.count() == 0:
            return None

        title = await title_el.inner_text()
        url = await title_el.get_attribute("href") or ""

        excerpt_el = card.locator(".RichContent-inner, .content")
        excerpt = ""
        if await excerpt_el.count() > 0:
            excerpt = await excerpt_el.inner_text()
            excerpt = excerpt[:200] + "..." if len(excerpt) > 200 else excerpt

        author_el = card.locator(".AuthorInfo-name, .UserLink-link")
        author = ""
        if await author_el.count() > 0:
            author = await author_el.inner_text()

        item_type = "unknown"
        if "/question/" in url:
            if "/answer/" in url:
                item_type = "answer"
            else:
                item_type = "question"
        elif "/p/" in url or "zhuanlan" in url:
            item_type = "article"
        elif "/people/" in url:
            item_type = "people"

        vote_el = card.locator(".VoteButton--up")
        vote_count = 0
        if await vote_el.count() > 0:
            vote_text = await vote_el.inner_text()
            vote_count = _parse_vote_count(vote_text)

        comment_el = card.locator('button:has-text("评论"), a:has-text("评论")')
        comment_count = 0
        if await comment_el.count() > 0:
            comment_text = await comment_el.first.inner_text()
            comment_count = _parse_comment_count(comment_text)

        item_id = url.split("/")[-1] if url else ""

        return SearchResult(
            id=item_id,
            type=item_type,
            title=title.strip(),
            excerpt=excerpt.strip(),
            author=author.strip() or None,
            url=url,
            vote_count=vote_count,
            comment_count=comment_count,
        )
    except Exception:
        return None


def _parse_vote_count(text: str) -> int:
    """
    解析赞同数文本（支持万、k 等单位）。

    Args:
        text: 赞同数文本，如 "1.2 万"、"5k"。

    Returns:
        数值。
    """
    text = text.strip()
    if not text:
        return 0

    text = text.replace("赞同", "").replace(" ", "")
    if "万" in text:
        num = float(text.replace("万", ""))
        return int(num * 10000)
    elif "k" in text.lower():
        num = float(text.lower().replace("k", ""))
        return int(num * 1000)
    else:
        try:
            return int(text)
        except ValueError:
            return 0


def _parse_comment_count(text: str) -> int:
    """
    解析评论数文本。

    Args:
        text: 评论数文本，如 "12 条评论"。

    Returns:
        数值。
    """
    import re

    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1))
    return 0


async def extract_question_detail(page: Page) -> dict:
    """
    从问题页面提取问题详情。

    Args:
        page: Playwright 页面对象。

    Returns:
        包含 title、detail、answer_count 的字典。
    """
    title_el = page.locator("h1.QuestionHeader-title").first
    title = await title_el.inner_text() if await title_el.count() > 0 else ""

    detail_el = page.locator(".QuestionRichText, .QuestionHeader-detail").first
    detail = await detail_el.inner_text() if await detail_el.count() > 0 else ""

    answer_count_el = page.locator(".List-headerText")
    answer_count = 0
    if await answer_count_el.count() > 0:
        text = await answer_count_el.inner_text()
        import re

        match = re.search(r"(\d+)", text)
        if match:
            answer_count = int(match.group(1))

    return {
        "title": title.strip(),
        "detail": detail.strip(),
        "answer_count": answer_count,
    }


async def extract_answer_by_id(page: Page, answer_id: int | str) -> dict | None:
    """
    根据 ID 提取特定回答。

    Args:
        page: Playwright 页面对象。
        answer_id: 回答 ID。

    Returns:
        包含回答信息的字典或 None。
    """
    answer_el = page.locator(
        f'[data-za-index][data-zop-feedwr="{answer_id}"], [data-id="{answer_id}"]'
    )
    if await answer_el.count() > 0:
        return await _extract_answer_content(answer_el.first)

    items = await page.locator(".List-item").all()
    for item in items:
        data_id = await item.get_attribute("data-id") or await item.get_attribute(
            "data-zop-feedwr"
        )
        if data_id and str(data_id) == str(answer_id):
            return await _extract_answer_content(item)

    content_el = page.locator(".RichContent-inner")
    if await content_el.count() > 0:
        return await _extract_answer_from_page(page)

    return None


async def _extract_answer_from_page(page: Page) -> dict:
    """
    从回答详情页面提取回答内容。

    Args:
        page: Playwright 页面对象。

    Returns:
        包含回答信息的字典。
    """
    author_el = page.locator(".AuthorInfo-name").first
    author = await author_el.inner_text() if await author_el.count() > 0 else ""

    content_el = page.locator(".RichContent-inner").first
    content = ""
    if await content_el.count() > 0:
        content = await content_el.inner_html()

    vote_el = page.locator(".VoteButton--up").first
    vote_count = 0
    if await vote_el.count() > 0:
        vote_text = await vote_el.inner_text()
        vote_count = _parse_vote_count(vote_text)

    comment_el = page.locator('button:has-text("评论")').first
    comment_count = 0
    if await comment_el.count() > 0:
        comment_text = await comment_el.inner_text()
        comment_count = _parse_comment_count(comment_text)

    return {
        "author": author.strip(),
        "content": content,
        "vote_count": vote_count,
        "comment_count": comment_count,
    }


async def _extract_answer_content(item) -> dict:
    """
    从回答元素提取内容。

    Args:
        item: 回答元素定位器。

    Returns:
        包含回答信息的字典。
    """
    author_el = item.locator(".AuthorInfo-name")
    author = await author_el.inner_text() if await author_el.count() > 0 else ""

    content_el = item.locator(".RichContent-inner")
    content = ""
    if await content_el.count() > 0:
        content = await content_el.inner_html()

    vote_el = item.locator(".VoteButton--up")
    vote_count = 0
    if await vote_el.count() > 0:
        vote_text = await vote_el.inner_text()
        vote_count = _parse_vote_count(vote_text)

    comment_el = item.locator('button:has-text("评论")')
    comment_count = 0
    if await comment_el.count() > 0:
        comment_text = await comment_el.first.inner_text()
        comment_count = _parse_comment_count(comment_text)

    return {
        "author": author.strip(),
        "content": content,
        "vote_count": vote_count,
        "comment_count": comment_count,
    }


async def extract_all_answers(page: Page) -> list[dict]:
    """
    提取问题页面所有回答。

    Args:
        page: Playwright 页面对象。

    Returns:
        回答信息字典列表。
    """
    answers: list[dict] = []

    await page.wait_for_selector(".List-item", timeout=10000)
    items = await page.locator(".List-item").all()

    for item in items:
        answer = await _extract_answer_content(item)
        if answer and answer.get("content"):
            answers.append(answer)

    return answers


async def extract_article_content(page: Page) -> dict:
    """
    从文章页面提取文章内容。

    Args:
        page: Playwright 页面对象。

    Returns:
        包含文章信息的字典。
    """
    title_el = page.locator("h1.Post-Title, .Post-Title").first
    title = await title_el.inner_text() if await title_el.count() > 0 else ""

    author_el = page.locator(".AuthorInfo-name").first
    author = await author_el.inner_text() if await author_el.count() > 0 else ""

    content_el = page.locator(".Post-RichText").first
    content = ""
    if await content_el.count() > 0:
        content = await content_el.inner_html()

    vote_el = page.locator(".VoteButton--up").first
    vote_count = 0
    if await vote_el.count() > 0:
        vote_text = await vote_el.inner_text()
        vote_count = _parse_vote_count(vote_text)

    comment_el = page.locator('button:has-text("评论")').first
    comment_count = 0
    if await comment_el.count() > 0:
        comment_text = await comment_el.inner_text()
        comment_count = _parse_comment_count(comment_text)

    return {
        "title": title.strip(),
        "author": author.strip(),
        "content": content,
        "vote_count": vote_count,
        "comment_count": comment_count,
    }


async def extract_answers(page: Page) -> list[dict]:
    """
    提取回答列表（简化版，仅返回文本内容）。

    Args:
        page: Playwright 页面对象。

    Returns:
        回答信息字典列表。
    """
    answers: list[dict] = []

    await page.wait_for_selector(".List-item", timeout=10000)
    items = await page.locator(".List-item").all()

    for item in items:
        answer = await _extract_answer_item(item)
        if answer:
            answers.append(answer)

    return answers


async def _extract_answer_item(item) -> dict | None:
    """
    从回答元素提取简化信息。

    Args:
        item: 回答元素定位器。

    Returns:
        包含回答信息的字典或 None。
    """
    try:
        author_el = item.locator(".AuthorInfo-name")
        author = await author_el.inner_text() if await author_el.count() > 0 else ""

        content_el = item.locator(".RichContent-inner")
        content = await content_el.inner_text() if await content_el.count() > 0 else ""

        vote_el = item.locator(".VoteButton--up")
        vote_count = 0
        if await vote_el.count() > 0:
            vote_text = await vote_el.inner_text()
            vote_count = _parse_vote_count(vote_text)

        return {
            "author": author.strip(),
            "content": content.strip(),
            "vote_count": vote_count,
        }
    except Exception:
        return None
