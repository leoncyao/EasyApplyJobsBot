import json
import time
import argparse
import os
import random
from dotenv import load_dotenv
from .pychrome_applier import PyChromeJobApplier
from .login import connect_to_chrome, login_to_linkedin
from .utils import _print
from .constants import constants

# Load environment variables
load_dotenv()

class BatchJobApplier:
    def __init__(self, retry_failed=False, verbose=False, browser=None, tab=None):
        self.applied_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.browser = browser
        self.tab = tab
        self.successful_applications = 0

    def load_job_urls(self, json_file='data/job_data.json'):
        """Load job URLs from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            _print(f"❌ Job URLs file not found: {json_file}", level="error", verbose=self.verbose)
            return {}
        except json.JSONDecodeError:
            _print(f"❌ Invalid JSON file: {json_file}", level="error", verbose=self.verbose)
            return {}

    def process_jobs(self):
        """Process all jobs in the job_data.json file"""
        try:
            # Load job data
            if not os.path.exists('data/job_data.json'):
                _print("❌ No job data file found. Please run the scraper first.", level="error", verbose=self.verbose)
                return False

            with open('data/job_data.json', 'r', encoding='utf-8') as f:
                job_data = json.load(f)

            _print(f"\n📊 Starting batch application process", level="info", verbose=self.verbose)
            _print(f"📊 Total jobs to process: {len(job_data)}", level="info", verbose=self.verbose)
            _print(f"📊 Target successful applications: {constants.max_successful_applications}", level="info", verbose=self.verbose)

            self.applier = PyChromeJobApplier(browser=self.browser, tab=self.tab, verbose=self.verbose)
            # Process each job
            _print(f" Successfully created applier", level="info", verbose=self.verbose)
            _print(f" job_data.items {len(job_data.items())}", level="info", verbose=self.verbose)
            for job_id, job_info in job_data.items():
                # Check if we've reached the maximum number of successful applications
                if self.successful_applications >= constants.max_successful_applications:
                    _print(f"\n✅ Reached maximum number of successful applications ({constants.max_successful_applications})", level="success", verbose=self.verbose)
                    break

                # Skip if already applied and not retrying failed
                already_applied = False
                if job_info['status'] == 'applied':
                    _print(f"⏭️ Skipping job: {job_info['url']} (already applied)", level="info", verbose=self.verbose)
                    self.skipped_count += 1
                    already_applied = True
                    continue
                elif job_info['status'] == 'failed' and not self.retry_failed:
                    _print(f"⏭️ Skipping job: {job_info['url']} (previously failed)", level="info", verbose=self.verbose)
                    self.skipped_count += 1
                    continue

                _print(f"\n🔄 Processing job: {job_info['url']}", level="info", verbose=self.verbose)
                _print(f"📊 Current successful applications: {self.successful_applications}/{constants.max_successful_applications}", level="info", verbose=self.verbose)
                _print(f"📊 Current stats - Applied: {self.successful_applications}, Failed: {self.failed_count}, Skipped: {self.skipped_count}", level="info", verbose=self.verbose)

                # Apply to job
                if self.applier.apply_to_job(job_info['url']):
                    job_info['status'] = 'applied'
                    if not already_applied:
                        self.successful_applications += 1
                    _print(f"✅ Successfully applied! ({self.successful_applications}/{constants.max_successful_applications} successful applications)", level="success", verbose=self.verbose)
                else:
                    job_info['status'] = 'failed'
                    _print(f"❌ Failed to apply. ({self.successful_applications}/{constants.max_successful_applications} successful applications)", level="error", verbose=self.verbose)

                # Save updated job data
                with open('data/job_data.json', 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)

                # Add delay between applications
                time.sleep(random.uniform(0.1, constants.botSpeed))

            _print(f"\n=== Final Summary ===", level="info", verbose=self.verbose)
            _print(f"✅ Total jobs processed: {len(job_data)}", level="success", verbose=self.verbose)
            _print(f"✅ Successfully applied to: {self.successful_applications}/{constants.max_successful_applications} jobs", level="success", verbose=self.verbose)
            return True

        except Exception as e:
            _print(f"❌ Error processing jobs: {str(e)}", level="error", verbose=self.verbose)
            return False

    def _print_progress(self):
        """Print current progress"""
        total = self.applied_count + self.failed_count + self.skipped_count
        _print(f"\nProgress: {total} jobs processed", level="info", verbose=self.verbose)
        _print(f"✅ Applied: {self.applied_count}", level="success", verbose=self.verbose)
        _print(f"❌ Failed: {self.failed_count}", level="error", verbose=self.verbose)
        _print(f"⚠️ Skipped: {self.skipped_count}", level="info", verbose=self.verbose)

    def _print_final_summary(self):
        """Print final summary"""
        _print("\n=== Final Summary ===", level="info", verbose=self.verbose)
        _print(f"✅ Successfully applied: {self.applied_count}", level="success", verbose=self.verbose)
        _print(f"❌ Failed applications: {self.failed_count}", level="error", verbose=self.verbose)
        _print(f"⚠️ Skipped jobs: {self.skipped_count}", level="info", verbose=self.verbose)
        _print(f"Total jobs processed: {self.applied_count + self.failed_count + self.skipped_count}", level="info", verbose=self.verbose)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch apply to LinkedIn jobs from JSON file')
    parser.add_argument('--email', default=os.getenv('EMAIL'), help='LinkedIn email (defaults to .env)')
    parser.add_argument('--password', default=os.getenv('PASSWORD'), help='LinkedIn password (defaults to .env)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get credentials from .env if not provided via command line
    email = args.email or os.getenv('EMAIL')
    password = args.password or os.getenv('PASSWORD')
    
    if not email or not password:
        print("Error: LinkedIn credentials not found. Please provide them via command line arguments or in .env file")
        exit(1)
    
    try:
        # First connect to Chrome and login
        browser, tab = connect_to_chrome(verbose=args.verbose)
        if not browser or not tab:
            print("Error: Failed to connect to Chrome")
            exit(1)


        login_to_linkedin(tab, email, password, args.verbose)
            
        # if not login_to_linkedin(tab, email, password, args.verbose):
            # print("Error: Failed to login to LinkedIn")
            # exit(1)
            
        # Initialize and start batch processing
        batch_applier = BatchJobApplier(verbose=args.verbose)
        batch_applier.process_jobs()
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1) 