

"""
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
"""

from playwright.sync_api import sync_playwright
import json
import time
import os

def extract_job_titles_from_urls(urls, auth_file="linkedin_auth.json", headless=True, delay=1.5):
    job_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=auth_file)
        page = context.new_page()

        for url in urls:
            try:
                print(f"→ Visiting {url}")
                page.goto(url, timeout=60000)
                page.wait_for_selector("h1.t-24.t-bold", timeout=10000)
                el = page.query_selector("h1.t-24.t-bold")
                title = el.inner_text().strip() if el else "Title not found"
            except Exception as e:
                title = f"Error: {e!s}"
            job_data.append({"url": url, "title": title})
            time.sleep(delay)

        browser.close()
    return job_data

if __name__ == "__main__":
    # 1) Load all URLs from your job_links JSON
    links_path = "linkedin_jobs.json"
    if not os.path.exists(links_path):
        raise FileNotFoundError(f"{links_path} not found—run your scraper first.")
    with open(links_path, "r", encoding="utf-8") as f:
        job_links = json.load(f).get("job_links", [])

    # 2) Load existing titles (if any)
    titles_path = "linkedin_job_titles.json"
    if os.path.exists(titles_path):
        with open(titles_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    # Build a set of URLs we've already scraped
    scraped_urls = { entry["url"] for entry in existing }

    # 3) Filter to only the URLs that are new
    to_scrape = [url for url in job_links if url not in scraped_urls]
    print(f"Found {len(to_scrape)} new URL(s) to scrape.")

    # 4) Scrape only the new ones
    new_entries = extract_job_titles_from_urls(to_scrape, headless=True)

    # 5) Combine old + new, then save
    combined = existing + new_entries
    with open(titles_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=4, ensure_ascii=False)

    print(f"Total titles stored: {len(combined)}")