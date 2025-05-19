import time, random, json, os
import utils, constants, config
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from utils import prRed, prYellow, prGreen

class LinkedInUrlScraper:
    def __init__(self, driver=None):
        self.driver = driver
        # Initialize empty JSON file
        if not os.path.exists('data'):
            os.makedirs('data')
        with open('data/job_urls.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        prGreen("✅ Initialized job_urls.json file")

    def _process_job_page(self, url, page_number):
        """Process a single page of job listings"""
        current_page_jobs = constants.jobsPerPage * page_number
        page_url = f"{url}&start={current_page_jobs}"
        self.driver.get(page_url)
        time.sleep(random.uniform(0.1, constants.botSpeed))
        
        offers = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
        return [(offer.get_attribute("data-occludable-job-id").split(":")[-1]) for offer in offers]

    def scrape_job_urls(self):
        """Main method to scrape job URLs"""
        if not os.path.exists('data'):
            os.makedirs('data')

        # Initialize empty JSON file
        with open('data/job_urls.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        prGreen("✅ Initialized job_urls.json file")

        job_urls = []
        url = "https://www.linkedin.com/jobs/search/?currentJobId=4229987963&f_AL=true&f_E=2f_SB2&f_JT=F%2CP%2CC&f_WT=1%2C2%2C3&geoId=100761630&keywords=software%20developer&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true&sortBy=DD"
        print(f"Processing URL: {url}")
        self.driver.get(url)
        time.sleep(5)

        for page in range(2):
            page_jobs = self._process_job_page(url, page)
            if not page_jobs:
                break

            for job_id in page_jobs:
                job_url = f'https://www.linkedin.com/jobs/view/{job_id}'
                job_urls.append({
                    'url': job_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })

            # Save after each page
            with open('data/job_urls.json', 'w', encoding='utf-8') as f:
                json.dump(job_urls, f, indent=2, ensure_ascii=False)
            prGreen(f"✅ Updated job_urls.json with {len(job_urls)} jobs")

        return job_urls

    def _process_job_page(self, url, page_number):
        """Process a single page of job listings"""
        current_page_jobs = 25 * page_number
        page_url = f"{url}&start={current_page_jobs}"
        self.driver.get(page_url)
        # time.sleep(random.uniform(0.1, constants.botSpeed))

        time.sleep(5)
        
        offers = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
        return [(offer.get_attribute("data-occludable-job-id").split(":")[-1]) for offer in offers]

    def _save_job_urls(self, job_urls):
        """Save job URLs to a JSON file"""
        try:
            with open('data/job_urls.json', 'w', encoding='utf-8') as f:
                json.dump(job_urls, f, indent=2, ensure_ascii=False)
            prGreen("✅ Job URLs saved successfully to data/job_urls.json")
        except Exception as e:
            prRed(f"❌ Error saving job URLs: {str(e)}")

    def close(self):
        """Close the browser"""
        self.driver.quit()

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description='Scrape LinkedIn job URLs')
#     parser.add_argument('--email', default=config.email, help='LinkedIn email')
#     parser.add_argument('--password', default=config.password, help='LinkedIn password')
#     parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
#     args = parser.parse_args()
    
#     scraper = LinkedInUrlScraper(email=args.email, password=args.password, headless=args.headless)
#     try:
#         scraper.scrape_job_urls()
#     finally:
#         scraper.close() 