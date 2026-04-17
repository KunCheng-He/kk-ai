"""
登录辅助模块。

提供交互式登录和认证状态检查功能。
"""

import asyncio
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page

from zhihu_utils.browser import (
    create_browser_context,
    apply_stealth,
    save_auth_state,
    check_login_status,
    AUTH_FILE,
    ZHIHU_HOME,
)


class AuthenticationError(Exception):
    """认证失败异常。"""

    pass


async def login_interactive(headless: bool = False) -> Path:
    """
    交互式登录，等待用户手动完成登录后保存认证状态。

    Args:
        headless: 是否使用无头模式，登录时建议使用有头模式。

    Returns:
        认证文件路径。

    Raises:
        AuthenticationError: 登录超时或失败时抛出。
    """
    browser, context = await create_browser_context(headless=headless)
    page = await context.new_page()
    await apply_stealth(page)

    try:
        await page.goto(ZHIHU_HOME)
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


async def ensure_authenticated(
    headless: bool = True,
) -> tuple[Browser, BrowserContext, Page]:
    """
    确保已认证，如果认证失效则提示重新登录。

    Args:
        headless: 是否使用无头模式。

    Returns:
        (Browser, BrowserContext, Page) 元组。

    Raises:
        AuthenticationError: 认证失效且无法自动恢复时抛出。
    """
    browser, context = await create_browser_context(headless=headless)
    page = await context.new_page()
    await apply_stealth(page)

    try:
        is_logged_in = await check_login_status(page)
        if is_logged_in:
            return browser, context, page

        await browser.close()

        if headless:
            raise AuthenticationError(
                "认证已失效，请运行 `uv run python main.py --login` 重新登录。"
            )

        await login_interactive(headless=False)
        browser, context = await create_browser_context(headless=headless)
        page = await context.new_page()
        await apply_stealth(page)

        is_logged_in = await check_login_status(page)
        if is_logged_in:
            return browser, context, page

        raise AuthenticationError("登录后仍无法通过认证，请检查账号状态。")

    except Exception as e:
        await browser.close()
        raise


async def main():
    """登录助手入口。"""
    import argparse

    parser = argparse.ArgumentParser(description="知乎登录助手")
    parser.add_argument("--login", action="store_true", help="执行交互式登录")
    parser.add_argument("--check", action="store_true", help="检查当前登录状态")
    args = parser.parse_args()

    if args.login:
        await login_interactive(headless=False)
    elif args.check:
        browser, context = await create_browser_context(headless=True)
        page = await context.new_page()
        await apply_stealth(page)

        try:
            is_logged_in = await check_login_status(page)
            status = "已登录" if is_logged_in else "未登录或认证已失效"
            print(f"当前状态: {status}")
            if is_logged_in:
                print(f"认证文件: {AUTH_FILE}")
        finally:
            await browser.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
