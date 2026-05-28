import os
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth


CACHE_DIR = Path.home() / ".cache" / "xhs-k-search"
AUTH_FILE = CACHE_DIR / "auth.json"
XHS_HOME = "https://www.xiaohongshu.com"
CDP_URL = "http://localhost:9222"


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


async def create_cdp_context(
    cdp_url: str = CDP_URL,
) -> tuple[Browser, BrowserContext, Page]:
    if "localhost" in cdp_url or "127.0.0.1" in cdp_url:
        proxy_keys = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                       "http_proxy", "https_proxy", "all_proxy")
        saved = {}
        for key in proxy_keys:
            if key in os.environ:
                saved[key] = os.environ.pop(key)
        try:
            p = await async_playwright().start()
            browser = await p.chromium.connect_over_cdp(cdp_url)
        finally:
            os.environ.update(saved)
    else:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(cdp_url)

    context = browser.contexts[0]
    page = await context.new_page()
    return browser, context, page


class XHSBrowser:
    def __init__(
        self,
        use_cdp: bool = True,
        headless: bool = True,
        cdp_url: str = CDP_URL,
        auth_file: Path | None = None,
    ):
        self.use_cdp = use_cdp
        self.headless = headless
        self.cdp_url = cdp_url
        self.auth_file = auth_file or AUTH_FILE
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self._playwright = None

    async def __aenter__(self):
        if self.use_cdp:
            self.browser, self.context, self.page = await create_cdp_context(self.cdp_url)
            self._playwright = None
        else:
            self._playwright = await async_playwright().start()
            stealth = Stealth()
            stealth.hook_playwright_context(self._playwright)

            self.browser = await self._playwright.chromium.launch(headless=self.headless)

            if self.auth_file.exists():
                self.context = await self.browser.new_context(storage_state=str(self.auth_file))
            else:
                self.context = await self.browser.new_context()

            self.page = await self.context.new_page()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser and not self.use_cdp:
            await self.browser.close()
        if self._playwright and not self.use_cdp:
            await self._playwright.stop()


async def save_auth_state(
    context: BrowserContext, path: str | Path | None = None
) -> None:
    save_path = path or AUTH_FILE
    _ensure_cache_dir()
    await context.storage_state(path=str(save_path))


async def check_login_status(page: Page) -> bool:
    await page.goto(XHS_HOME)
    await page.wait_for_load_state("networkidle")

    try:
        await page.wait_for_selector(
            '[class*="user"] a[href*="user"]', timeout=5000
        )
        return True
    except Exception:
        pass

    try:
        login_btn = page.locator('button:has-text("登录"), text="登录"')
        if await login_btn.count() > 0:
            return False
    except Exception:
        pass

    user_menu = page.locator('[class*="user"], [class*="User"], [class*="profile"]')
    return await user_menu.count() > 0
