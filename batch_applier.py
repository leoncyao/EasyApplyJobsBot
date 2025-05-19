import json
import time
import argparse
from job_applier import JobApplier
from utils import prRed, prYellow, prGreen

class BatchJobApplier:
    def __init__(self, driver, max_applications=None, delay_between_applications=3):
        self.driver = driver
        self.max_applications = max_applications
        self.delay_between_applications = delay_between_applications
        self.applied_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def load_job_urls(self, json_file='data/job_urls.json'):
        """Load job URLs from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            prRed(f"❌ Job URLs file not found: {json_file}")
            return []
        except json.JSONDecodeError:
            prRed(f"❌ Invalid JSON file: {json_file}")
            return []

    def process_jobs(self):
        """Process all jobs from the JSON file"""
        job_urls = self.load_job_urls()
        if not job_urls:
            return

        total_jobs = len(job_urls)
        prYellow(f"Found {total_jobs} jobs to process")
        applier = JobApplier(
            driver=self.driver,
        )
        for job in job_urls:
            if self.max_applications and self.applied_count >= self.max_applications:
                prYellow(f"Reached maximum number of applications ({self.max_applications})")
                break

            prYellow(f"\nProcessing job URL: {job['url']}")
            prYellow(f"Found at: {job['timestamp']}")

            try:
                success = applier.apply_to_job(job['url'])
                if success:
                    self.applied_count += 1
                    prGreen(f"✅ Successfully applied to job")
                else:
                    self.skipped_count += 1
                    prYellow(f"⚠️ Skipped job")
            except Exception as e:
                self.failed_count += 1
                prRed(f"❌ Failed to apply to job: {str(e)}")

                # # Print progress
                # self._print_progress()

                # Wait between applications
                if self.delay_between_applications > 0:
                    prYellow(f"Waiting {self.delay_between_applications} seconds before next application...")
                    time.sleep(self.delay_between_applications)

        self._print_final_summary()

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
    parser.add_argument('--email', required=True, help='LinkedIn email')
    parser.add_argument('--password', required=True, help='LinkedIn password')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--max', type=int, help='Maximum number of applications to submit')
    parser.add_argument('--delay', type=int, default=60, help='Delay between applications in seconds')
    parser.add_argument('--json', default='data/job_urls.json', help='Path to JSON file containing job URLs')
    
    args = parser.parse_args()
    
    batch_applier = BatchJobApplier(
        email=args.email,
        password=args.password,
        headless=args.headless,
        max_applications=args.max,
        delay_between_applications=args.delay
    )
    
    batch_applier.process_jobs() 