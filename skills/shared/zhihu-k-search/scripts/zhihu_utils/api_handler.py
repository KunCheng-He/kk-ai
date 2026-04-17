"""
API 请求处理模块。

通过拦截浏览器网络请求获取知乎 API 响应，实现搜索、问题、回答、文章等数据获取。
优先使用 API 拦截方式，DOM 提取作为备用方案。
"""

import json
import urllib.parse
from typing import Any
from playwright.async_api import Page, Request, Response
from zhihu_utils.data_models import (
    SearchResult,
    Answer,
    Question,
    Article,
    SearchResponse,
    SearchType,
)


SEARCH_API_URL = "https://www.zhihu.com/api/v4/search_v3"
GRAPHQL_URL = "https://www.zhihu.com/graphql"


class APIHandler:
    """知乎 API 处理器，负责拦截和解析 API 响应。"""

    def __init__(self, page: Page):
        """
        初始化 API 处理器。

        Args:
            page: Playwright 页面对象。
        """
        self.page = page
        self.captured_responses: list[dict[str, Any]] = []
        self._setup_interceptor()

    def _setup_interceptor(self) -> None:
        """设置响应拦截器。"""
        self.page.on("response", self._on_response)

    async def _on_response(self, response: Response) -> None:
        """
        响应拦截回调，捕获搜索和 GraphQL API 响应。

        Args:
            response: 响应对象。
        """
        url = response.url
        if "api/v4/search" in url or "graphql" in url:
            try:
                if response.ok:
                    data = await response.json()
                    self.captured_responses.append(
                        {"url": url, "data": data, "status": response.status}
                    )
            except Exception:
                pass

    def clear_captured(self) -> None:
        """清空已捕获的响应列表。"""
        self.captured_responses.clear()

    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.ALL,
        offset: int = 0,
        limit: int = 20,
    ) -> SearchResponse:
        """
        执行搜索请求。

        Args:
            query: 搜索关键词。
            search_type: 搜索类型。
            offset: 分页偏移量。
            limit: 返回结果数量限制。

        Returns:
            SearchResponse 对象。
        """
        self.clear_captured()

        encoded_query = urllib.parse.quote(query)
        type_param = search_type.value if search_type != SearchType.ALL else ""

        search_url = f"{SEARCH_API_URL}?t=general&q={encoded_query}&correction=1&offset={offset}&limit={limit}"
        if type_param:
            search_url += f"&type={type_param}"

        await self.page.goto(search_url, wait_until="networkidle")

        if self.captured_responses:
            return self._parse_search_response(
                query, self.captured_responses[0]["data"]
            )

        return await self._extract_from_dom(query)

    def _parse_search_response(
        self, query: str, data: dict[str, Any]
    ) -> SearchResponse:
        """
        解析搜索 API 响应。

        Args:
            query: 搜索关键词。
            data: API 响应数据。

        Returns:
            SearchResponse 对象。
        """
        results: list[SearchResult] = []

        items = data.get("data", [])
        for item in items:
            result = self._parse_search_item(item)
            if result:
                results.append(result)

        paging = data.get("paging", {})
        is_end = paging.get("is_end", True)
        next_url = paging.get("next", "")

        next_offset = None
        if not is_end and next_url:
            parsed = urllib.parse.urlparse(next_url)
            params = urllib.parse.parse_qs(parsed.query)
            if "offset" in params:
                next_offset = int(params["offset"][0])

        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
            has_more=not is_end,
            next_offset=next_offset,
        )

    def _parse_search_item(self, item: dict[str, Any]) -> SearchResult | None:
        """
        解析单个搜索结果项。

        Args:
            item: 单个搜索结果数据。

        Returns:
            SearchResult 对象或 None。
        """
        item_type = item.get("type", "")
        obj = item.get("object", item)
        highlight = item.get("highlight", {})

        if item_type == "search_result":
            obj = item.get("object", {})
            item_type = obj.get("type", item.get("type", ""))

        if item_type in ("answer", "article", "question", "people"):
            return self._create_search_result(obj, item_type, highlight)

        return None

    def _create_search_result(
        self,
        obj: dict[str, Any],
        item_type: str,
        highlight: dict[str, Any] | None = None,
    ) -> SearchResult:
        """
        创建 SearchResult 对象。

        Args:
            obj: 原始数据对象。
            item_type: 内容类型。
            highlight: 高亮信息。

        Returns:
            SearchResult 对象。
        """
        highlight = highlight or {}
        item_id = obj.get("id", "")

        title = highlight.get("title", "")
        if not title:
            if item_type == "answer":
                question = obj.get("question", {}) or {}
                title = question.get("title", "") or obj.get("title", "")
            elif item_type == "question":
                title = obj.get("title", "")
            elif item_type == "article":
                title = obj.get("title", "")
            elif item_type == "people":
                title = obj.get("name", "")

        title = self._strip_html_tags(title)

        excerpt = (
            highlight.get("description", "")
            or obj.get("excerpt", "")
            or obj.get("headline", "")
        )
        excerpt = self._strip_html_tags(excerpt)

        author = None
        if item_type in ("answer", "article"):
            author_info = obj.get("author", {})
            author = author_info.get("name", "")
        elif item_type == "people":
            author = obj.get("name", "")

        url = obj.get("url", "")
        if url and url.startswith("https://api.zhihu.com/"):
            url = ""
        if not url:
            if item_type == "answer":
                question_id = obj.get("question", {}).get("id", "")
                url = f"https://www.zhihu.com/question/{question_id}/answer/{item_id}"
            elif item_type == "question":
                url = f"https://www.zhihu.com/question/{item_id}"
            elif item_type == "article":
                url = f"https://zhuanlan.zhihu.com/p/{item_id}"
            elif item_type == "people":
                url_token = obj.get("url_token", "")
                url = f"https://www.zhihu.com/people/{url_token}"

        vote_count = obj.get("voteup_count", 0) or 0
        comment_count = obj.get("comment_count", 0) or 0

        return SearchResult(
            id=str(item_id),
            type=item_type,
            title=title,
            excerpt=excerpt,
            author=author,
            url=url,
            vote_count=vote_count,
            comment_count=comment_count,
        )

    @staticmethod
    def _strip_html_tags(text: str) -> str:
        """
        移除 HTML 标签。

        Args:
            text: 包含 HTML 标签的文本。

        Returns:
            纯文本。
        """
        import re

        return re.sub(r"<[^>]+>", "", text)

    async def _extract_from_dom(self, query: str) -> SearchResponse:
        """
        从 DOM 提取搜索结果（备用方案）。

        Args:
            query: 搜索关键词。

        Returns:
            SearchResponse 对象。
        """
        from zhihu_utils.extractors import extract_search_results

        results = await extract_search_results(self.page)
        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
            has_more=False,
        )

    async def get_question(self, question_id: int) -> Question | None:
        """
        获取问题详情。

        Args:
            question_id: 问题 ID。

        Returns:
            Question 对象或 None。
        """
        url = f"https://www.zhihu.com/question/{question_id}"
        self.clear_captured()

        await self.page.goto(url, wait_until="networkidle")

        for resp in self.captured_responses:
            data = resp.get("data", {})
            if isinstance(data, dict) and "title" in data and "answer_count" in data:
                return self._parse_question(data)

        from zhihu_utils.extractors import extract_question_detail

        detail = await extract_question_detail(self.page)
        if detail.get("title"):
            return Question(
                id=question_id,
                title=detail.get("title", ""),
                detail=detail.get("detail", ""),
                answer_count=detail.get("answer_count", 0),
                follower_count=0,
                url=f"https://www.zhihu.com/question/{question_id}",
            )

        return None

    def _parse_question(self, data: dict[str, Any]) -> Question:
        """
        解析问题数据。

        Args:
            data: API 响应数据。

        Returns:
            Question 对象。
        """
        return Question(
            id=data.get("id", 0),
            title=data.get("title", ""),
            detail=data.get("detail", ""),
            answer_count=data.get("answer_count", 0),
            follower_count=data.get("follower_count", 0),
            url=f"https://www.zhihu.com/question/{data.get('id', 0)}",
        )

    async def get_answers(
        self,
        question_id: int,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "default",
    ) -> list[Answer]:
        """
        获取问题的回答列表。

        Args:
            question_id: 问题 ID。
            offset: 分页偏移量。
            limit: 返回回答数量限制。
            sort_by: 排序方式。

        Returns:
            Answer 对象列表。
        """
        url = f"https://www.zhihu.com/question/{question_id}"
        self.clear_captured()

        await self.page.goto(url, wait_until="networkidle")

        from zhihu_utils.extractors import extract_all_answers

        answers_data = await extract_all_answers(self.page)

        answers: list[Answer] = []
        for i, ans_data in enumerate(answers_data[:limit]):
            answers.append(
                Answer(
                    id=0,
                    question_id=question_id,
                    question_title="",
                    content=ans_data.get("content", ""),
                    excerpt="",
                    author_name=ans_data.get("author", ""),
                    author_url_token="",
                    vote_count=ans_data.get("vote_count", 0),
                    comment_count=ans_data.get("comment_count", 0),
                    url=f"https://www.zhihu.com/question/{question_id}",
                )
            )

        for resp in self.captured_responses:
            data = resp.get("data", {})
            items = (
                data
                if isinstance(data, list)
                else [data]
                if isinstance(data, dict)
                else []
            )
            for item in items:
                if item.get("type") == "answer" and item.get("id"):
                    for ans in answers:
                        if not ans.id:
                            ans.id = item.get("id", 0)
                            question = item.get("question", {})
                            ans.question_title = question.get("title", "")
                            author = item.get("author", {})
                            if not ans.author_name:
                                ans.author_name = author.get("name", "")
                            break

        return answers

    def _parse_answers(self, items: list[dict[str, Any]]) -> list[Answer]:
        """
        解析回答列表数据。

        Args:
            items: API 响应数据列表。

        Returns:
            Answer 对象列表。
        """
        answers: list[Answer] = []
        for item in items:
            answer = self._parse_answer(item)
            if answer:
                answers.append(answer)
        return answers

    def _parse_answer(self, data: dict[str, Any]) -> Answer | None:
        """
        解析单个回答数据。

        Args:
            data: API 响应数据。

        Returns:
            Answer 对象或 None。
        """
        if not data:
            return None

        question = data.get("question", {})
        author = data.get("author", {})

        return Answer(
            id=data.get("id", 0),
            question_id=question.get("id", 0),
            question_title=question.get("title", ""),
            content=data.get("content", ""),
            excerpt=data.get("excerpt", ""),
            author_name=author.get("name", ""),
            author_url_token=author.get("url_token", ""),
            vote_count=data.get("voteup_count", 0) or 0,
            comment_count=data.get("comment_count", 0) or 0,
            url=f"https://www.zhihu.com/question/{question.get('id', 0)}/answer/{data.get('id', 0)}",
        )

    async def get_answer(
        self, answer_id: int, question_id: int | None = None
    ) -> Answer | None:
        """
        获取单个回答详情。

        Args:
            answer_id: 回答 ID。
            question_id: 问题 ID（可选）。

        Returns:
            Answer 对象或 None。
        """
        if not question_id:
            return None

        url = f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}"
        self.clear_captured()

        await self.page.goto(url, wait_until="networkidle")

        from zhihu_utils.extractors import extract_answer_by_id

        answer_data = await extract_answer_by_id(self.page, answer_id)
        if not answer_data:
            return None

        for resp in self.captured_responses:
            data = resp.get("data", {})
            items = (
                data
                if isinstance(data, list)
                else [data]
                if isinstance(data, dict)
                else []
            )
            for item in items:
                if item.get("id") == answer_id:
                    question = item.get("question", {})
                    author = item.get("author", {})
                    return Answer(
                        id=item.get("id", 0),
                        question_id=question.get("id", question_id),
                        question_title=question.get("title", ""),
                        content=answer_data.get("content", ""),
                        excerpt=item.get("excerpt", ""),
                        author_name=author.get("name", answer_data.get("author", "")),
                        author_url_token=author.get("url_token", ""),
                        vote_count=item.get("voteup_count", 0)
                        or answer_data.get("vote_count", 0),
                        comment_count=item.get("comment_count", 0)
                        or answer_data.get("comment_count", 0),
                        url=f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}",
                    )

        return Answer(
            id=answer_id,
            question_id=question_id,
            question_title="",
            content=answer_data.get("content", ""),
            excerpt="",
            author_name=answer_data.get("author", ""),
            author_url_token="",
            vote_count=answer_data.get("vote_count", 0),
            comment_count=answer_data.get("comment_count", 0),
            url=f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}",
        )

    async def get_article(self, article_id: str | int) -> Article | None:
        """
        获取文章详情。

        Args:
            article_id: 文章 ID。

        Returns:
            Article 对象或 None。
        """
        url = f"https://zhuanlan.zhihu.com/p/{article_id}"
        self.clear_captured()

        await self.page.goto(url, wait_until="networkidle")

        from zhihu_utils.extractors import extract_article_content

        article_data = await extract_article_content(self.page)
        if not article_data:
            return None

        for resp in self.captured_responses:
            data = resp.get("data", {})
            if isinstance(data, dict) and data.get("id"):
                author = data.get("author", {})
                return Article(
                    id=str(data.get("id", article_id)),
                    title=data.get("title", article_data.get("title", "")),
                    content=article_data.get("content", ""),
                    excerpt=data.get("excerpt", ""),
                    author_name=author.get("name", article_data.get("author", "")),
                    author_url_token=author.get("url_token", ""),
                    vote_count=data.get("voteup_count", 0)
                    or article_data.get("vote_count", 0),
                    comment_count=data.get("comment_count", 0)
                    or article_data.get("comment_count", 0),
                    url=f"https://zhuanlan.zhihu.com/p/{article_id}",
                )

        return Article(
            id=str(article_id),
            title=article_data.get("title", ""),
            content=article_data.get("content", ""),
            excerpt="",
            author_name=article_data.get("author", ""),
            author_url_token="",
            vote_count=article_data.get("vote_count", 0),
            comment_count=article_data.get("comment_count", 0),
            url=f"https://zhuanlan.zhihu.com/p/{article_id}",
        )

    def _parse_article(self, data: dict[str, Any]) -> Article:
        """
        解析文章数据。

        Args:
            data: API 响应数据。

        Returns:
            Article 对象。
        """
        author = data.get("author", {})

        return Article(
            id=str(data.get("id", "")),
            title=data.get("title", ""),
            content=data.get("content", ""),
            excerpt=data.get("excerpt", ""),
            author_name=author.get("name", ""),
            author_url_token=author.get("url_token", ""),
            vote_count=data.get("voteup_count", 0) or 0,
            comment_count=data.get("comment_count", 0) or 0,
            url=f"https://zhuanlan.zhihu.com/p/{data.get('id', '')}",
        )

    async def get_question_with_answers(
        self,
        question_id: int,
        answer_limit: int = 5,
        sort_by: str = "default",
    ) -> dict[str, Any] | None:
        """
        获取问题及其回答列表。

        Args:
            question_id: 问题 ID。
            answer_limit: 返回回答数量限制。
            sort_by: 排序方式。

        Returns:
            包含 question 和 answers 的字典，或 None。
        """
        question = await self.get_question(question_id)
        if not question:
            return None

        answers = await self.get_answers(
            question_id, limit=answer_limit, sort_by=sort_by
        )

        return {
            "question": question,
            "answers": answers,
        }
