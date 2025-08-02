"""
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

title = "Software Developer"

list_url = "https://www.linkedin.com/jobs/search-results/?keywords=software%20developer"

response = requests.get(list_url)

list_data = response.text
list_soup = BeautifulSoup(list_data, "html.parser")
page_jobs = list_soup.find_all("ul")

list_job = []

for job in page_jobs:
    base_card_div = job.find("div", {"class": "scaffold-layout__list"})
    list_job.append(base_card_div)

base_card_div = job.find("div", {"class": "scaffold-layout__list"})

print(page_jobs)
print(base_card_div)
print(response)

job-card-job-posting-card-wrapper__card-link
"""

"""
https://www.linkedin.com/jobs/search/?distance=25&keywords=software%20developer
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import OrderedDict
import os
import json

def load_existing_links(filename="linkedin_jobs.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("job_links", [])

def scrape_linkedin_jobs_with_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="linkedin_auth.json")
        page = context.new_page()

        page.goto("https://www.linkedin.com/jobs/search/?distance=25&keywords=software%20engineer", timeout=60000)

        # More robust: wait for any job card to appear
        page.wait_for_selector("a.job-card-container__link", timeout=35000)

        for _ in range(5):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")


    job_links = []
    job_data = []

    for a_tag in soup.select("a.job-card-container__link[href]"):
        href = a_tag.get("href")
        title = a_tag.get_text(strip=True)

        if "/jobs" in href:
            full_url = "https://www.linkedin.com" + href.split("?")[0]

            job_links.append(full_url)
            job_data.append({
                "title": title,
                "url": full_url
            })
    
    if len(job_links) != len(set(job_links)):
        print("Duplicates found.")
    else:
        print("No duplicates.")

    existing_links = load_existing_links("linkedin_jobs.json")


    # Combine and deduplicate
    all_links = list(OrderedDict.fromkeys(existing_links + job_links))
    

    print(f"Found {len(job_links)} job links.")

    new_urls = [url for url in job_links if url not in existing_links]

    print(f"Found {len(new_urls)} new job links.")

    print(f"Total stored job links: {len(all_links)}")

    with open("linkedin_jobs.json", "w", encoding="utf-8") as f:
        json.dump({
            "job_links": all_links,
            "newly_added": new_urls,
            "job_data": job_data
        }, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    scrape_linkedin_jobs_with_login()