import argparse
import time
from login import connect_to_chrome, login_to_linkedin
from pychrome_batch_applier import BatchJobApplier
from pychrome_scraper import PyChromeLinkedInScraper
import config
from utils import _print

def run_bot(email, password, skip_login=False, skip_scraping=False, retry_failed=False, verbose=False):
    """Run the complete LinkedIn bot process using Chrome DevTools Protocol"""
    print("\n=== Bot Configuration ===")
    print(f"[INFO] Log Level: {config.log_level}")
    print(f"[INFO] Email: {email}")
    print(f"[INFO] Skip Login: {skip_login}")
    print(f"[INFO] Skip Scraping: {skip_scraping}")
    print(f"[INFO] Retry Failed: {retry_failed}")
    print(f"[INFO] Verbose: {verbose}")
    print("=======================\n")

    browser = None
    tab = None
    
    try:
        # Connect to Chrome and login
        print("\n=== Connecting to Chrome and Logging in ===")
        browser, tab = connect_to_chrome(verbose=verbose)
        if not browser or not tab:
            print("Error: Failed to connect to Chrome")
            return False
            
        if not skip_login:
            if not login_to_linkedin(tab, email, password, verbose):
                print("Error: Failed to login to LinkedIn")
                return False
        else:
            print("Skipping LinkedIn login as requested")

        # Scrape URLs if not skipped
        if not skip_scraping:
            print("\n=== Scraping Job URLs ===")
            scraper = PyChromeLinkedInScraper(browser, tab, verbose=verbose)
            scraper.scrape_job_urls()
        else:
            print("Skipping URL scraping as requested")

        # Apply to jobs
        print("\n=== Starting Batch Application Process ===")
        batch_applier = BatchJobApplier(
            browser=browser,
            tab=tab,
            retry_failed=retry_failed,
            verbose=verbose,
        )
        batch_applier.process_jobs()

        return True

    except Exception as e:
        print(f"Error in bot execution: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Bot')
    parser.add_argument('--email', default=config.email, help='LinkedIn email (defaults to config.py)')
    parser.add_argument('--password', default=config.password, help='LinkedIn password (defaults to config.py)')
    parser.add_argument('--skip-scraping', action='store_true', help='Skip URL scraping and use existing job_urls.json')
    parser.add_argument('--retry-failed', action='store_true', help='Retry failed applications')
    parser.add_argument('--skip-login', action='store_true', help='Skip LinkedIn login (useful if already logged in)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get credentials from config.py if not provided via command line
    email = args.email or config.email
    password = args.password or config.password
    
    if not args.skip_login and (not email or not password):
        print("Error: LinkedIn credentials not found. Please provide them via command line arguments or in config.py")
        exit(1)

    success = run_bot(
        email=email,
        password=password,
        skip_login=args.skip_login,
        skip_scraping=args.skip_scraping,
        retry_failed=args.retry_failed,
        verbose=args.verbose,
    )

    exit(0 if success else 1) 