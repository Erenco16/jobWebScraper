from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time
import json

BASE_URL = "https://gradireland.com"
START_URL = f"{BASE_URL}/graduate-jobs"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Remote(
    command_executor=os.getenv("GRID_URL", "http://selenium-hub:4444/wd/hub"),
    options=options
)

driver.get(START_URL)
time.sleep(5)

# Get job links
soup = BeautifulSoup(driver.page_source, "html.parser")
job_cards = soup.find_all("a", {"data-cy": "card:view-opportunity"})
job_links = [BASE_URL + a['href'] for a in job_cards if a.get('href')]
print(f"Found {len(job_links)} job links.")

data = []

for link in job_links:
    print(f"Scraping: {link}")
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "space-y-4"))
        )
        time.sleep(2)
        job_soup = BeautifulSoup(driver.page_source, "html.parser")
        desc_container = job_soup.find("div", class_="space-y-4")
        if desc_container:
            text = desc_container.get_text(separator="\n", strip=True)
            data.append({
                "url": link,
                "description": text,
                "label": 1
            })
    except Exception as e:
        print(f"❌ Error scraping {link}: {e}")
        continue

driver.quit()

# Save to JSON
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
with open(os.path.join(output_dir, "gradireland_jobs.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Scraping complete. Data saved to gradireland_jobs.json")
