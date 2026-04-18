from pathlib import Path
from playwright.async_api import async_playwright


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

        await context.storage_state(path="auth.json")
        await browser.close()
        print("登录状态已保存到 auth.json")

    async def login_and_save(self, auth_file: Path):
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

            await context.storage_state(path=auth_file)
            await browser.close()
            print(f"登录状态已保存到 {auth_file}")
