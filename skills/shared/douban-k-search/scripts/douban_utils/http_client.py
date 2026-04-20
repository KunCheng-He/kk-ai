"""HTTP 请求客户端和 JSON 提取。"""

import asyncio
from typing import Any

import httpx

from douban_utils.data_models import Category, SearchResult

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

REQUEST_DELAY = 1.5
MAX_RETRIES = 3


class DoubanHttpClient:
    """豆瓣 HTTP 客户端。"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        self._last_request_time = 0.0

    async def close(self):
        await self.client.aclose()

    async def _request_with_delay(self, url: str) -> httpx.Response:
        """带延迟的请求，避免频率过高。"""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < REQUEST_DELAY:
            await asyncio.sleep(REQUEST_DELAY - elapsed)

        for attempt in range(MAX_RETRIES):
            try:
                self._last_request_time = asyncio.get_event_loop().time()
                response = await self.client.get(url)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise DoubanBlockedError("请求被拒绝，可能触发反爬") from e
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(REQUEST_DELAY * (attempt + 1))
            except httpx.RequestError:
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(REQUEST_DELAY * (attempt + 1))

        raise RuntimeError("unreachable")

    async def fetch_search_page(self, query: str, category: Category) -> str:
        """获取搜索页面 HTML。"""
        url = f"https://search.douban.com/{category.value}/subject_search?search_text={query}"
        response = await self._request_with_delay(url)
        return response.text

    async def fetch_detail_page(self, subject_id: int, category: Category) -> str:
        """获取详情页面 HTML。"""
        url = f"https://{category.value}.douban.com/subject/{subject_id}/"
        response = await self._request_with_delay(url)
        return response.text

    async def fetch_comments_page(self, subject_id: int, category: Category, start: int = 0) -> str:
        """获取短评页面 HTML。"""
        url = f"https://{category.value}.douban.com/subject/{subject_id}/comments?start={start}"
        response = await self._request_with_delay(url)
        return response.text


def extract_window_data(html: str) -> dict[str, Any] | None:
    """从 HTML 中提取 window.__DATA__ JSON 对象。"""
    import json

    start_marker = "window.__DATA__ = "
    start_idx = html.find(start_marker)
    if start_idx == -1:
        return None

    start_idx += len(start_marker)

    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(html[start_idx:], start_idx):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break

    json_str = html[start_idx:end_idx]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def parse_search_results(data: dict[str, Any], category: Category) -> list[SearchResult]:
    """解析搜索结果。"""
    results = []
    items = data.get("items", [])

    for item in items:
        rating = item.get("rating", {})
        result = SearchResult(
            id=item.get("id", 0),
            category=category,
            title=item.get("title", ""),
            url=item.get("url", ""),
            cover_url=item.get("cover_url"),
            rating_value=rating.get("value"),
            rating_count=rating.get("count", 0),
            abstract=item.get("abstract", ""),
        )
        results.append(result)

    return results


class DoubanBlockedError(Exception):
    """豆瓣请求被拒绝。"""

    pass
