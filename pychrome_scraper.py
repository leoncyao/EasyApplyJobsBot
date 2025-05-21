import time, random, json, os
import utils, constants, config
import pychrome
from utils import prRed, prYellow, prGreen

class PyChromeLinkedInScraper:
    def __init__(self, debugging_url="http://127.0.0.1:9222"):
        """Initialize the scraper with Chrome DevTools debugging URL"""
        self.debugging_url = debugging_url
        self.browser = None
        self.tab = None

    def connect(self):
        """Connect to Chrome and set up the tab"""
        try:
            self.browser = pychrome.Browser(url=self.debugging_url)
            print(self.browser)
            tabs = self.browser.list_tab()
            if not tabs:
                raise Exception("No tabs found in the browser")
            
            self.tab = tabs[0]
            self.tab.start()
            
            # Enable necessary domains
            self.tab.Network.enable()
            self.tab.Page.enable()
            self.tab.Runtime.enable()
            
            prGreen("✅ Successfully connected to Chrome")
            return True
        except Exception as e:
            prRed(f"❌ Failed to connect to Chrome: {str(e)}")
            return False

    def _process_job_page(self, url, page_number):
        """Process a single page of job listings"""
        current_page_jobs = constants.jobsPerPage * page_number
        page_url = f"{url}&start={current_page_jobs}"
        
        try:
            # Navigate to the page
            self.tab.Page.navigate(url=page_url)

            # time.sleep(random.uniform(0.1, constants.botSpeed))

            time.sleep(10)
        
            # If we found jobs with the original selector, use it
            script = """
            Array.from(document.querySelectorAll('li[data-occludable-job-id]'))
                .map(el => el.getAttribute('data-occludable-job-id'))
            """
            result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
            # prYellow(f"Raw result: {result}")  # Print the raw result
            
            # Try to get the value and print it
            value = result.get('result', {}).get('value', [])
            # prYellow(f"Extracted value: {value}")
            
            return value
            
        except Exception as e:
            prRed(f"❌ Error processing page {page_number}: {str(e)}")
            return []

    def scrape_job_urls(self):
        """Main method to scrape job URLs"""
        if not self.connect():
            return {}

        if not os.path.exists('data'):
            os.makedirs('data')

        # Load existing job data if available
        job_data = {}
        if os.path.exists('data/job_data.json'):
            try:
                with open('data/job_data.json', 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                prGreen(f"✅ Loaded {len(job_data)} existing jobs from job_data.json")
            except Exception as e:
                prRed(f"❌ Error loading existing job data: {str(e)}")
                job_data = {}

        url = "https://www.linkedin.com/jobs/search/?currentJobId=4229987963&f_AL=true&f_E=2f_SB2&f_JT=F%2CP%2CC&f_WT=1%2C2%2C3&geoId=100761630&keywords=software%20developer&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true&sortBy=DD"
        print(f"Processing URL: {url}")
        
        try:
            # Navigate to the initial page
            # self.tab.Page.navigate(url=url)
            # 
            time.sleep(random.uniform(0.1, constants.botSpeed))

            jobs_found = 0

            for page in range(6):
                page_jobs = self._process_job_page(url, page)
                if not page_jobs:
                    break

                for job_id in page_jobs:
                    # Only add new jobs that don't exist in job_data
                    if job_id not in job_data:
                        job_url = f'https://www.linkedin.com/jobs/view/{job_id}'
                        job_data[job_id] = {
                            'url': job_url,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'status': 'pending'
                        }
                        jobs_found += 1

                self._save_job_urls(job_data)

            prGreen(f"✅ Added {jobs_found} new jobs to job_data.json")
            return job_data

        except Exception as e:
            prRed(f"❌ Error during scraping: {str(e)}")
            return job_data

    def _save_job_urls(self, job_data):
        """Save job URLs to a JSON file"""
        try:
            with open('data/job_data.json', 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            prGreen("✅ Job URLs saved successfully to data/job_data.json")
        except Exception as e:
            prRed(f"❌ Error saving job URLs: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape LinkedIn job URLs using Chrome DevTools')
    parser.add_argument('--debug-url', default="http://localhost:9222", 
                      help='Chrome DevTools debugging URL (default: http://localhost:9222)')
    
    args = parser.parse_args()
    
    scraper = PyChromeLinkedInScraper(debugging_url=args.debug_url)
    try:
        scraper.scrape_job_urls()
    except Exception as e:
        print(f"error {e}")