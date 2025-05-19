import argparse
import time
from browser_manager import BrowserManager
from url_scraper import LinkedInUrlScraper
from batch_applier import BatchJobApplier
from utils import prRed, prYellow, prGreen
import config
class LinkedInBot:
    def __init__(self, email, password, headless=True, max_applications=None, delay=60, skip_scraping=False):
        self.email = email
        self.password = password
        self.headless = headless
        self.max_applications = max_applications
        self.delay = delay
        self.skip_scraping = skip_scraping
        self.browser = None

    def run(self):
        """Run the complete LinkedIn bot process"""
        try:
            # Initialize browser
            prYellow("\n=== Initializing Browser ===")
            self.browser = BrowserManager(self.email, self.password, self.headless)
            self.driver = self.browser.get_driver()

            # Scrape URLs if not skipped
            if not self.skip_scraping:
                prYellow("\n=== Scraping Job URLs ===")
                scraper = LinkedInUrlScraper(self.driver) # Use the same browser instance
                scraper.scrape_job_urls()
            else:
                prYellow("Skipping URL scraping as requested")

            # Apply to jobs
            prYellow("\n=== Starting Batch Application Process ===")
            batch_applier = BatchJobApplier(
                driver=self.driver,
                max_applications=self.max_applications,
                delay_between_applications=self.delay
            )
            batch_applier.process_jobs()

        except Exception as e:
            prRed(f"❌ Error in bot execution: {str(e)}")
        finally:
            if self.browser:
                self.browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Bot')
    parser.add_argument('--email', default=config.email, help='LinkedIn email')
    parser.add_argument('--password', default=config.password, help='LinkedIn password')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--max', type=int, help='Maximum number of applications to submit')
    parser.add_argument('--delay', type=int, default=60, help='Delay between applications in seconds')
    parser.add_argument('--skip-scraping', action='store_true', help='Skip URL scraping and use existing job_urls.json')
    
    args = parser.parse_args()
    
    bot = LinkedInBot(
        email=args.email,
        password=args.password,
        headless=args.headless,
        max_applications=args.max,
        delay=args.delay,
        skip_scraping=args.skip_scraping
    )
    
    bot.run() 