"""Playwright 浏览器管理。支持 CDP 模式和 Launch 模式。"""

import os

from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from playwright_stealth import Stealth

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


async def create_cdp_context(
    cdp_url: str = "http://localhost:9222",
) -> tuple[Browser, BrowserContext, Page]:
    """通过 CDP 连接到已有浏览器实例。

    无需启动新浏览器，直接复用已有浏览器的会话状态。
    当连接本地 CDP 时，临时移除代理环境变量以避免连接问题。

    Args:
        cdp_url: CDP 调试端点 URL，默认 localhost:9222。

    Returns:
        (Browser, BrowserContext, Page) 元组。
    """
    if "localhost" in cdp_url or "127.0.0.1" in cdp_url:
        _save = {}
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                     "http_proxy", "https_proxy", "all_proxy"):
            if key in os.environ:
                _save[key] = os.environ.pop(key)
        try:
            p = await async_playwright().start()
            browser = await p.chromium.connect_over_cdp(cdp_url)
        finally:
            os.environ.update(_save)
    else:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(cdp_url)

    context = browser.contexts[0]
    page = await context.new_page()
    return browser, context, page


class DoubanBrowser:
    """豆瓣浏览器客户端。支持 CDP 和 Launch 两种模式。"""

    def __init__(
        self,
        headless: bool = True,
        use_cdp: bool = True,
        cdp_url: str = "http://localhost:9222",
    ):
        self.headless = headless
        self.use_cdp = use_cdp
        self.cdp_url = cdp_url
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._is_cdp = False

    async def start(self):
        """启动或连接浏览器。"""
        if self.use_cdp:
            return await self._start_cdp()
        return await self._start_launch()

    async def _start_cdp(self):
        """通过 CDP 连接已有浏览器。"""
        self._browser, self._context, self._page = await create_cdp_context(self.cdp_url)
        self._is_cdp = True

    async def _start_launch(self):
        """启动独立浏览器。"""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        self._context = await self._browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        self._page = await self._context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(self._page)

    async def close(self):
        """关闭连接。CDP 模式下仅关闭新创建的 page，不关闭用户浏览器。"""
        if self._is_cdp:
            if self._page:
                try:
                    await self._page.close()
                except Exception:
                    pass
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
        else:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()

    async def fetch_page(self, url: str, wait_for: str | None = None) -> str:
        """获取页面 HTML。

        Args:
            url: 页面 URL。
            wait_for: 等待选择器。

        Returns:
            页面 HTML。
        """
        if not self._page:
            raise RuntimeError("浏览器未启动")

        await self._page.goto(url, wait_until="networkidle")

        if wait_for:
            await self._page.wait_for_selector(wait_for, timeout=30000)

        return await self._page.content()

    async def handle_pow_challenge(self):
        """处理 SHA-512 POW 验证。

        豆瓣电影详情页可能触发 POW 验证，需要等待自动计算完成。
        """
        if not self._page:
            return

        try:
            form = await self._page.query_selector("form[action*='submit']")
            if form:
                await self._page.wait_for_timeout(2000)
                submit_btn = await self._page.query_selector("input[type='submit']")
                if submit_btn:
                    await submit_btn.click()
                    await self._page.wait_for_load_state("networkidle")
        except Exception:
            pass

    async def fetch_movie_detail(self, subject_id: int) -> str:
        """获取电影详情页面。

        Args:
            subject_id: 条目 ID。

        Returns:
            页面 HTML。
        """
        url = f"https://movie.douban.com/subject/{subject_id}/"
        html = await self.fetch_page(url, wait_for="#info")

        if "验证" in html or "challenge" in html.lower():
            await self.handle_pow_challenge()
            html = await self._page.content()

        return html

    async def fetch_movie_comments(self, subject_id: int, start: int = 0) -> str:
        """获取电影短评页面。

        Args:
            subject_id: 条目 ID。
            start: 起始位置。

        Returns:
            页面 HTML。
        """
        url = f"https://movie.douban.com/subject/{subject_id}/comments?start={start}"
        return await self.fetch_page(url, wait_for=".comment-item")
