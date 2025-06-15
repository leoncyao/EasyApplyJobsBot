import time, random, json, os
import pychrome
from .utils import _print
from .constants import constants
from .config import linkedin_job_search_url

class PyChromeLinkedInScraper:
    def __init__(self, browser, tab, verbose=False):
        """Initialize the scraper with Chrome DevTools debugging URL"""
        self.browser = browser
        self.tab = tab
        self.verbose = verbose

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
            # _print(f"Raw result: {result}", level="debug", verbose=self.verbose)  # Print the raw result
            
            # Try to get the value and print it
            value = result.get('result', {}).get('value', [])
            # _print(f"Extracted value: {value}", level="debug", verbose=self.verbose)
            
            return value
            
        except Exception as e:
            _print(f"Error processing page {page_number}: {str(e)}", level="error", verbose=self.verbose)
            return []

    def _load_job_data(self):
        """Load existing job data from JSON file"""
        if not os.path.exists('data'):
            os.makedirs('data')

        job_data = {}
        if os.path.exists('data/job_data.json'):
            try:
                with open('data/job_data.json', 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                _print(f"Loaded {len(job_data)} existing jobs from job_data.json", level="success", verbose=self.verbose)
            except Exception as e:
                _print(f"Error loading existing job data: {str(e)}", level="error", verbose=self.verbose)
                job_data = {}
        return job_data

    def scrape_job_urls(self):
        """Main method to scrape job URLs"""
        url = linkedin_job_search_url
        _print(f"Scraping job URLs from {url}", level="info", verbose=self.verbose)
        job_data = self._load_job_data()
        jobs_found = 0
        max_new_jobs = 200  # Maximum number of new jobs to add
        
        try:
            # Navigate to the initial page
            time.sleep(random.uniform(0.1, constants.botSpeed))

            for page in range(0, 150):
                # Check if we've reached the maximum number of URLs based on total jobs looked at
                # total_jobs_looked_at = constants.jobsPerPage * page
                # if total_jobs_looked_at >= constants.max_urls:
                #     _print(f"Reached maximum URL limit of {constants.max_urls} (looked at {total_jobs_looked_at} jobs)", level="info", verbose=self.verbose)
                #     break

                # Check if we've reached the maximum number of new jobs
                if jobs_found >= max_new_jobs:
                    _print(f"Reached maximum limit of {max_new_jobs} new jobs", level="info", verbose=self.verbose)
                    break

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
                        _print(f"Job {job_id} added to job_data.json ({jobs_found}/{max_new_jobs})", level="info", verbose=self.verbose)
                        
                        # Check if we've reached the maximum number of new jobs
                        if jobs_found >= max_new_jobs:
                            break
                    else:
                        _print(f"Job {job_id} already exists in job_data.json", level="info", verbose=self.verbose)

                self._save_job_urls(job_data)

            _print(f"Added {jobs_found} new jobs to job_data.json", level="success", verbose=self.verbose)
            return job_data

        except Exception as e:
            _print(f"Error during scraping: {str(e)}", level="error", verbose=self.verbose)
            return job_data

    def _save_job_urls(self, job_data):
        """Save job URLs to a JSON file"""
        try:
            with open(constants.job_data_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            _print("✅ Job URLs saved successfully", level="success", verbose=self.verbose)
        except Exception as e:
            _print(f"❌ Error saving job URLs: {str(e)}", level="error", verbose=self.verbose)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape LinkedIn job URLs using Chrome DevTools')
    parser.add_argument('--debug-url', default="http://localhost:9222", 
                      help='Chrome DevTools debugging URL (default: http://localhost:9222)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    scraper = PyChromeLinkedInScraper(debugging_url=args.debug_url, verbose=args.verbose)
    try:
        scraper.scrape_job_urls()
    except Exception as e:
        _print(f"Error: {e}", level="error", verbose=True)