from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
from bs4 import BeautifulSoup

# Selenium Grid URL (from env var)
SELENIUM_GRID_URL = os.getenv("GRID_URL", "http://selenium-hub:4444/wd/hub")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Remote(
    command_executor=SELENIUM_GRID_URL,
    options=options
)

URL = "https://jobs.ericsson.com/careers?page=1&jobPipeline=careersite&start=0&location=ireland"
driver.get(URL)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

cards = soup.find_all("div", class_="cardContainer-GcY1a")
print(f"Found {len(cards)} job cards.")

for card in cards:
    a_tag = card.find("a", class_="r-link")
    if a_tag and a_tag.has_attr("id"):
        job_id = a_tag["id"].replace("job-card-", "")
        job_url = f"{URL}&pid={job_id}"
        print(job_url)
