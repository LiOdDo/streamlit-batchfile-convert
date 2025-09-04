# playwright_login.py
import json
import asyncio
from playwright.async_api import async_playwright

async def run(username, password, login_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        await page.goto(login_url)
        await page.fill('input#email', username)
        await page.fill('input#password', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        # Save cookies
        cookies = await context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)

        print("✅ Cookies saved to cookies.json")

        await browser.close()

if __name__ == "__main__":
    import sys
    username, password, login_url = sys.argv[1], sys.argv[2], sys.argv[3]
    asyncio.run(run(username, password, login_url))
