import json
from playwright.sync_api import sync_playwright

def run(username, password, login_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto(login_url)
        page.fill('input#email', username)
        page.fill('input#password', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Save cookies
        cookies = context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)

        print("✅ Cookies saved to cookies.json")

        browser.close()

if __name__ == "__main__":
    import sys
    username, password, login_url = sys.argv[1], sys.argv[2], sys.argv[3]
    run(username, password, login_url)
