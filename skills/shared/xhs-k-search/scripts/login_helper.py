import asyncio
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from playwright_stealth import Stealth

from xhs_utils.browser import (
    create_cdp_context,
    save_auth_state,
    check_login_status,
    AUTH_FILE,
    XHS_HOME,
    CDP_URL,
)


class AuthenticationError(Exception):
    pass


async def login_interactive(headless: bool = False) -> Path:
    p = await async_playwright().start()
    stealth = Stealth()
    stealth.hook_playwright_context(p)
    browser = await p.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(XHS_HOME)
        print("请在浏览器中完成登录（扫码或账号密码）...")
        print("登录成功后，脚本将自动检测并保存认证信息。")

        max_wait = 300
        poll_interval = 2
        elapsed = 0

        while elapsed < max_wait:
            is_logged_in = await check_login_status(page)
            if is_logged_in:
                await save_auth_state(context, AUTH_FILE)
                print(f"登录成功！认证信息已保存至: {AUTH_FILE}")
                return AUTH_FILE

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise AuthenticationError("登录超时，请重试。")

    finally:
        await browser.close()
        await p.stop()


async def ensure_authenticated(
    headless: bool = True,
    use_cdp: bool = True,
    cdp_url: str = CDP_URL,
) -> tuple[Browser, BrowserContext, Page]:
    """确保已认证，返回 (browser, context, page)，调用方负责关闭。"""
    if use_cdp:
        try:
            return await _ensure_cdp_connected(cdp_url)
        except Exception as e:
            raise AuthenticationError(
                f"CDP 连接失败: {e}\n请确保浏览器已以调试模式启动（远程调试端口 9222）。\n"
                f"具体步骤请参考 SKILL.md 中的说明。"
            ) from e

    p = await async_playwright().start()
    stealth = Stealth()
    stealth.hook_playwright_context(p)

    browser = await p.chromium.launch(headless=headless)

    try:
        context = await _create_context(browser)
        page = await context.new_page()

        is_logged_in = await check_login_status(page)
        if is_logged_in:
            return browser, context, page

        await browser.close()
        browser = None

        if headless:
            raise AuthenticationError(
                "认证已失效，请运行 `uv run python main.py login` 重新登录。"
            )

        await login_interactive(headless=False)

        browser = await p.chromium.launch(headless=headless)
        context = await _create_context(browser)
        page = await context.new_page()

        is_logged_in = await check_login_status(page)
        if is_logged_in:
            return browser, context, page

        raise AuthenticationError("登录后仍无法通过认证，请检查账号状态。")

    except Exception as e:
        if browser is not None:
            await browser.close()
        await p.stop()
        raise


async def _create_context(browser: Browser) -> BrowserContext:
    if AUTH_FILE.exists():
        return await browser.new_context(storage_state=str(AUTH_FILE))
    return await browser.new_context()


async def _ensure_cdp_connected(
    cdp_url: str = CDP_URL,
) -> tuple[Browser, BrowserContext, Page]:
    return await create_cdp_context(cdp_url)
