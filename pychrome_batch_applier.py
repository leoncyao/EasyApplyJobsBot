import json
import time
import argparse
import os
import random
from pychrome_applier import PyChromeJobApplier
from utils import prRed, prYellow, prGreen
import config
from login import connect_to_chrome, login_to_linkedin

from utils import _print

class BatchJobApplier:
    def __init__(self, retry_failed=False, verbose=False, browser=None, tab=None):
        self.applied_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.browser = browser
        self.tab = tab

    def load_job_urls(self, json_file='data/job_data.json'):
        """Load job URLs from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            prRed(f"❌ Job URLs file not found: {json_file}")
            return {}
        except json.JSONDecodeError:
            prRed(f"❌ Invalid JSON file: {json_file}")
            return {}

    def process_jobs(self):
        """Process all jobs in the queue"""
        if not os.path.exists('data'):
            os.makedirs('data')

        # Load job data from JSON file
        job_data = self.load_job_urls()
        if not job_data:
            prRed("❌ No jobs to process")
            return

        prYellow(f"📋 Found {len(job_data)} jobs to process")

        # Initialize or load failed applications file
        failed_apps_file = 'data/failed_applications.json'
        if os.path.exists(failed_apps_file):
            with open(failed_apps_file, 'r', encoding='utf-8') as f:
                failed_apps = json.load(f)
        else:
            failed_apps = {}

        # Initialize or load application results file
        results_file = 'data/application_results.json'
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            results = []

        # Initialize JobApplier
        self.applier = PyChromeJobApplier(self.browser, self.tab)

        for job_id, job in job_data.items():
            try:
                _print(f"\n🔄 Processing job: {job['url']}", level="info", verbose=self.verbose)
                
                # Check job status
                if job.get('status') == 'applied':
                    _print(f"✅ Already applied to {job['url']}", level="info", verbose=self.verbose)
                    continue
                elif job.get('status') == 'failed' and not self.retry_failed:
                    _print(f"⚠️ Skipping previously failed job: {job['url']}", level="info", verbose=self.verbose)
                    continue
                print(job['url'])
                success = self.applier.apply_to_job(job['url'])
                
                # Update job status in job_data.json
                job_data[job_id]['status'] = 'applied' if success else 'failed'

                # Save updated job_data.json
                with open('data/job_data.json', 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)
                
                # Log the result
                result = {
                    'job_id': job_id,
                    'url': job['url'],
                    'success': success,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)
                
                # Save results after each job
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                if not success:
                    # Add to failed applications if not already there
                    if job_id not in failed_apps:
                        failed_apps[job_id] = job_data[job_id]
                        with open(failed_apps_file, 'w', encoding='utf-8') as f:
                            json.dump(failed_apps, f, indent=2, ensure_ascii=False)
                        prRed(f"❌ Added to failed applications: {job['url']}")
                
                time.sleep(random.uniform(1, 3))  # Random delay between jobs
                
            except Exception as e:
                prRed(f"❌ Error processing job {job['url']}: {str(e)}")
                # Add to failed applications
                if job_id not in failed_apps:
                    failed_apps[job_id] = job_data[job_id]
                    with open(failed_apps_file, 'w', encoding='utf-8') as f:
                        json.dump(failed_apps, f, indent=2, ensure_ascii=False)
                continue

    def _print_progress(self):
        """Print current progress"""
        total = self.applied_count + self.failed_count + self.skipped_count
        prYellow(f"\nProgress: {total} jobs processed")
        prGreen(f"✅ Applied: {self.applied_count}")
        prRed(f"❌ Failed: {self.failed_count}")
        prYellow(f"⚠️ Skipped: {self.skipped_count}")

    def _print_final_summary(self):
        """Print final summary"""
        prYellow("\n=== Final Summary ===")
        prGreen(f"✅ Successfully applied: {self.applied_count}")
        prRed(f"❌ Failed applications: {self.failed_count}")
        prYellow(f"⚠️ Skipped jobs: {self.skipped_count}")
        prYellow(f"Total jobs processed: {self.applied_count + self.failed_count + self.skipped_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch apply to LinkedIn jobs from JSON file')
    parser.add_argument('--email', default=config.email, help='LinkedIn email (defaults to config.py)')
    parser.add_argument('--password', default=config.password, help='LinkedIn password (defaults to config.py)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get credentials from config.py if not provided via command line
    email = args.email or config.email
    password = args.password or config.password
    
    if not email or not password:
        print("Error: LinkedIn credentials not found. Please provide them via command line arguments or in config.py")
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