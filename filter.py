import json
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def filter_active_jobs(input_file="linkedin_jobs.json", output_file="active_linkedin_jobs.json"):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        urls = data.get("job_links", [])

    active_urls = []
    removed_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Checking: {url}")
            try:
                page.goto(url, timeout=20000)
                page.wait_for_timeout(3000)

                # Look for specific LinkedIn class that shows closed jobs
                selector = "span.artdeco-inline-feedback__message"
                if page.locator(selector).is_visible():
                    text = page.locator(selector).inner_text().strip().lower()
                    if "no longer accepting applications" in text:
                        print("Inactive job found")
                        removed_urls.append(url)
                        continue

                active_urls.append(url)

            except PlaywrightTimeoutError:
                print("Timeout loading page, keeping URL just in case.")
                active_urls.append(url)
            except Exception as e:
                print(f"Error loading page: {e}")
                active_urls.append(url)

        browser.close()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"job_links": active_urls}, f, indent=2)

    with open("inactive_linkedin_jobs.json", "w", encoding="utf-8") as f:
        json.dump({"job_links": removed_urls}, f, indent=2)

    print(f"Done. {len(active_urls)} active jobs saved to '{output_file}'.")
    print(f"{len(removed_urls)} inactive jobs saved to 'inactive_linkedin_jobs.json'.")

# Run the function
filter_active_jobs()
