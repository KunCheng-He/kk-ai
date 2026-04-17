"""
浏览器管理模块。

提供 Playwright 浏览器上下文创建、反爬虫配置、认证状态管理等功能。
"""

import json
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth


AUTH_FILE = Path(__file__).parent.parent / "auth.json"
ZHIHU_HOME = "https://www.zhihu.com"


async def create_browser_context(
    headless: bool = True,
    storage_state: str | Path | None = None,
) -> tuple[Browser, BrowserContext]:
    """
    创建浏览器实例和上下文。

    Args:
        headless: 是否使用无头模式。
        storage_state: 认证状态文件路径，默认使用 AUTH_FILE。

    Returns:
        (Browser, BrowserContext) 元组。
    """
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
    )

    state_path = storage_state or AUTH_FILE
    if Path(state_path).exists():
        await _load_storage_state(context, state_path)

    return browser, context


async def _load_storage_state(context: BrowserContext, state_path: str | Path) -> None:
    """
    从文件加载存储状态（cookies 和 localStorage）。

    Args:
        context: 浏览器上下文。
        state_path: 状态文件路径。
    """
    with open(state_path) as f:
        state = json.load(f)

    if "cookies" in state:
        await context.add_cookies(state["cookies"])

    if "origins" in state:
        for origin in state["origins"]:
            origin_url = origin.get("origin", "https://www.zhihu.com")
            page = await context.new_page()
            await page.goto(origin_url)
            for item in origin.get("localStorage", []):
                await page.evaluate(
                    f"localStorage.setItem('{item['name']}', '{item['value']}')"
                )
            await page.close()


async def apply_stealth(page: Page) -> None:
    """
    对页面应用反检测配置，隐藏自动化特征。

    Args:
        page: Playwright 页面对象。
    """
    stealth = Stealth()
    await stealth.apply_stealth_async(page)


async def save_auth_state(
    context: BrowserContext, path: str | Path | None = None
) -> None:
    """
    保存认证状态到文件。

    Args:
        context: 浏览器上下文。
        path: 保存路径，默认使用 AUTH_FILE。
    """
    save_path = path or AUTH_FILE
    await context.storage_state(path=str(save_path))


async def check_login_status(page: Page) -> bool:
    """
    检查当前登录状态。

    Args:
        page: Playwright 页面对象。

    Returns:
        True 表示已登录，False 表示未登录。
    """
    await page.goto(ZHIHU_HOME)
    await page.wait_for_load_state("networkidle")

    try:
        await page.wait_for_selector(
            '[data-za-detail-view-path-module="UserInfo"]', timeout=5000
        )
        return True
    except Exception:
        pass

    try:
        sign_btn = page.locator('button:has-text("登录"), button:has-text("Sign in")')
        if await sign_btn.count() > 0:
            return False
    except Exception:
        pass

    user_menu = page.locator('.AppHeader-profile, .UserLink, [class*="Profile"]')
    return await user_menu.count() > 0
