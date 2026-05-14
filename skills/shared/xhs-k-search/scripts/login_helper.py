from pathlib import Path
from playwright.async_api import async_playwright

from xhs_utils.browser import AUTH_FILE, _ensure_cache_dir


class LoginHelper:
    def __init__(self):
        self.xhs_url = "https://www.xiaohongshu.com/"

    async def _login(self, playwright):
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(self.xhs_url)
        print("请在打开的浏览器中完成登录...")
        print("登录成功后，请按回车键继续...")

        input()

        _ensure_cache_dir()
        await context.storage_state(path=str(AUTH_FILE))
        await browser.close()
        print(f"登录状态已保存到 {AUTH_FILE}")

    async def login_and_save(self, auth_file: Path | None = None):
        save_path = auth_file or AUTH_FILE
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(self.xhs_url)
            print("请在打开的浏览器中完成登录...")
            print("等待登录成功...")

            try:
                await page.wait_for_selector(
                    '[class*="user"] a[href*="user"]', timeout=300000
                )
            except Exception:
                await page.wait_for_timeout(300000)

            _ensure_cache_dir()
            await context.storage_state(path=str(save_path))
            await browser.close()
            print(f"登录状态已保存到 {save_path}")
