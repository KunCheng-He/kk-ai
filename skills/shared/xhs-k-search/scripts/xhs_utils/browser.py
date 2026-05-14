import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright
from playwright_stealth import Stealth


CACHE_DIR = Path.home() / ".cache" / "xhs-k-search"
AUTH_FILE = CACHE_DIR / "auth.json"


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


class XHSBrowser:
    def __init__(self, auth_file: Optional[Path] = None, headless: bool = True):
        self.auth_file = auth_file or AUTH_FILE
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright: Optional[Playwright] = None
        self.page = None

    async def _init_browser(self):
        stealth = Stealth()
        playwright = await async_playwright().start()
        stealth.hook_playwright_context(playwright)

        browser = await playwright.chromium.launch(headless=self.headless)

        if self.auth_file.exists():
            context = await browser.new_context(storage_state=str(self.auth_file))
        else:
            _ensure_cache_dir()
            context = await browser.new_context()

        page = await context.new_page()

        return playwright, browser, context, page

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            asyncio.run(self.browser.close())

    async def __aenter__(self):
        (
            self.playwright,
            self.browser,
            self.context,
            self.page,
        ) = await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
