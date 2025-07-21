from playwright.sync_api import sync_playwright

def login_and_save_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Logging in to LinkedIn manually...")
        page.goto("https://www.linkedin.com/login")

        # Allow time to log in fully
        input("Press ENTER only after you see your LinkedIn homepage...")

        # Save cookies/local storage for next session
        context.storage_state(path="linkedin_auth.json")
        browser.close()
        print("Session saved to linkedin_auth.json")

if __name__ == "__main__":
    login_and_save_state()
