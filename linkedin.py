import time,math,random,os
import utils,constants,config
import code
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils import prRed,prYellow,prGreen

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys

import argparse

class Linkedin:
    def __init__(self, email=config.email, password=config.password, jobID=-1, headless=True):
            prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
            chrome_options = utils.chromeBrowserOptions()
            print(f'headless {headless}')
            if headless:
                chrome_options.add_argument("--headless")
            
            # Add these lines to disable GPU and WebGL warnings
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
            chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
            chrome_options.add_argument("--disable-dev-shm-usage")  # Reduce shared memory usage
            chrome_options.add_argument("--no-sandbox")  # Disable sandbox (common in containers)
            chrome_options.add_argument("--log-level=3")  # Suppress all but fatal errors
            chrome_options.add_argument("--silent")  # Reduce console output
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Disable verbose ChromeDriver logs
                        
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
            # self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=utils.chromeBrowserOptions())
            self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")

            prYellow("🔄 Trying to log in Linkedin...")
            if jobID != -1:
                self.url = 'https://www.linkedin.com/jobs/view/' + str(jobID)
            else:
                self.url = ""
            # self.url = "https://www.linkedin.com/jobs/view/4228206289/"
            # self.url = "https://www.linkedin.com/jobs/view/4230419609/"
            self.url = "https://www.linkedin.com/jobs/view/4228688053/"
            
            print(email)
            # password = "x/q+/6*GM7,Uvst"
            # neonleonyao@gmail.com
            print(password)
            try:    
                self.driver.find_element("id","username").send_keys(email)
                time.sleep(1)
                self.driver.find_element("id","password").send_keys(password)
                time.sleep(1)
                self.driver.find_element("xpath",'//button[@type="submit"]').click()
                time.sleep(2)
                self.linkJobApply()
            except Exception as e:
                prRed(e)
                prRed("❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")
    
    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try: 
            with open('data/urlData.txt', 'w',encoding="utf-8" ) as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url+ "\n")
            prGreen("✅ Apply urls are created successfully, now the bot will visit those urls.")
        except:
            prRed("❌ Couldn't generate urls, make sure you have editted config file line 25-39")

    def _process_job_page(self, url, page_number):
        """Process a single page of job listings"""
        current_page_jobs = constants.jobsPerPage * page_number
        page_url = f"{url}&start={current_page_jobs}"
        self.driver.get(page_url)
        time.sleep(random.uniform(1, constants.botSpeed))
        
        offers = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
        return [(offer.get_attribute("data-occludable-job-id").split(":")[-1]) for offer in offers]

    def _process_single_job(self, job_id, count_jobs, url_words):
        """Process a single job application"""
        offer_page = self.url if self.url else f'https://www.linkedin.com/jobs/view/{job_id}'
        self.driver.get(offer_page)
        time.sleep(random.uniform(1, constants.botSpeed))

        job_properties = self.getJobProperties(count_jobs)
        
        if "blacklisted" in job_properties:
            self._handle_blacklisted_job(job_properties, offer_page)
            return False

        return self._handle_job_application(job_properties, offer_page)

    def _handle_blacklisted_job(self, job_properties, offer_page):
        """Handle blacklisted job cases"""
        line_to_write = f"{job_properties} | * 🤬 Blacklisted Job, skipped!: {offer_page}"
        self.displayWriteResults(line_to_write)

    def _handle_job_application(self, job_properties, offer_page):
        """Handle the job application process"""
        easy_apply_button = self.easyApplyButton()
        
        if not easy_apply_button:
            line_to_write = f"{job_properties} | * 🥳 Already applied! Job: {offer_page}"
            self.displayWriteResults(line_to_write)
            return False

        try:
            easy_apply_button.click()
            time.sleep(random.uniform(1, constants.botSpeed))
            
            if self._complete_application_process():
                return True
            else:
                self._handle_failed_application(job_properties, offer_page)
                return False
                
        except Exception as e:
            prRed(f"Error during application process: {str(e)}")
            return False

    def _complete_application_process(self):
        """Complete the multi-step application process"""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                
                continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
                continue_button.click()
                time.sleep(random.uniform(1, constants.botSpeed))

                self.chooseResume()
                time.sleep(random.uniform(1, constants.botSpeed))
                
                self.applyProcess()
                time.sleep(random.uniform(1, constants.botSpeed))
                
                attempt += 1
            except Exception as e:
                print(f"Error in application step: {e}")
                break

        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
            submit_button.click()
            return True
        except:
            return False

    def _handle_failed_application(self, job_properties, offer_page):
        """Handle failed application cases"""
        line_to_write = f"{job_properties} | * 🥵 Cannot apply to this Job! {offer_page}"
        self.displayWriteResults(line_to_write)
        with open('data/url_fail_cases.txt', 'a') as g:
            g.write(f"\n{offer_page}\n")

    def linkJobApply(self):
        """Main function to handle job applications"""
        self.generateUrls()
        count_applied = 0
        count_jobs = 0

        url_data = utils.getUrlDataFile()

        for url in url_data:
            print(f"Processing URL: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            url_words = utils.urlToKeywords(url)

            for page in range(10):
                job_ids = self._process_job_page(url, page)
                
                for job_id in job_ids:
                    count_jobs += 1
                    if self._process_single_job(job_id, count_jobs, url_words):
                        count_applied += 1
                    
                    if self.url:  # If specific job ID was provided, break after processing it
                        break

                if self.url:  # Break page loop if specific job ID was provided
                    break

            prYellow(f"Category: {url_words[0]}, {url_words[1]} applied: {count_applied} jobs out of {count_jobs}.")

        utils.donate(self)

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                resumes[0].click()
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                resumes[config.preferredCv-1].click()
            elif (type(len(resumes)) != int):
                prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account.")

            self.continueButton().click()
        except:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                prYellow("⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(5)
            jobDetail = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                print(e)
                prYellow("⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if (config.displayWarnings):
                print(e)
                prYellow("⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle +" | " + jobDetail + jobLocation
        return textToWrite

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.XPATH, "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]")
            EasyApplyButton = button
        except: 
            EasyApplyButton = False

        return EasyApplyButton

    def find_review_button(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            review_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']")
            return review_button
        except: 
            return False

    def continueButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
            ContinueButton = button
        except: 
            ContinueButton = False

        return ContinueButton

    def submitButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
            SubmitButton = button
        except: 
            SubmitButton = False

        return SubmitButton

    def handle_text_inputs(self, input_fields):
        """Handle text input fields in the application form"""
        for input_field in input_fields:
            if input_field.get_attribute("type") == "text":
                if "city" in input_field.get_attribute("id").lower():
                    self._handle_city_input(input_field)
                else:
                    self._handle_generic_text_input(input_field)

    def _handle_city_input(self, input_field):
        """Handle city-specific input field"""
        input_field.send_keys("Toronto")     
        time.sleep(random.uniform(1, constants.botSpeed))   
        input_field.send_keys(Keys.DOWN)        
        time.sleep(random.uniform(1, constants.botSpeed))       
        input_field.send_keys(Keys.ENTER) 

    def _handle_generic_text_input(self, input_field):
        """Handle generic text input fields"""
        if len(input_field.get_attribute("value")) == 0:
            input_field.send_keys("3")

    def handle_radio_inputs(self, input_fields):
        """Handle radio input fields in the application form"""
        radio_fields = [field for field in input_fields if field.get_attribute("type") == "radio" 
                       and "y" in field.get_attribute("value").lower()]
        
        for radio_field in radio_fields:
            ActionChains(self.driver).click(radio_field).perform()
            time.sleep(random.uniform(0.5, 1))

    def handle_fieldset_radio_inputs(self, dialog):
        """Handle radio inputs within fieldsets"""
        fieldsets = dialog.find_elements(By.TAG_NAME, "fieldset")
        for fieldset in fieldsets:
            radio_inputs = fieldset.find_elements(By.TAG_NAME, "input")
            for radio_input in radio_inputs:
                try:
                    if radio_input.get_attribute("type") == "radio":
                        self._click_radio_input(radio_input)
                except Exception as e:
                    print(f"Error clicking radio input: {str(e)}")
                    continue

    def _click_radio_input(self, radio_input):
        """Attempt to click a radio input using different methods"""
        try:
            radio_input.click()
        except:
            ActionChains(self.driver).click(radio_input).perform()
        time.sleep(random.uniform(0.5, 1))

    def handle_select_fields(self, dialog):
        """Handle select/dropdown fields in the application form"""
        select_fields = dialog.find_elements(By.TAG_NAME, "select")
        for select_field in select_fields:
            Select(select_field).select_by_index(1)

    def handle_follow_company(self):
        """Handle the follow company checkbox if enabled"""
        if config.followCompanies:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
            except:
                pass

    def applyProcess(self):
        """Main process for handling job application form"""
        max_attempts = 10
        i = 0

        while i < max_attempts:
            time.sleep(random.uniform(2, constants.botSpeed))
            i += 1

            # Save questions for reference
            questions = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
            with open('data/questions.txt', 'w') as f:
                for question in questions:
                    f.write(question.get_attribute("innerText"))

            # Get the application dialog
            dialog = self.driver.find_element(By.CSS_SELECTOR, "[data-test-modal-id='easy-apply-modal']")
            input_fields = dialog.find_elements(By.TAG_NAME, "input")

            # Handle different types of form inputs
            self.handle_text_inputs(input_fields)
            self.handle_radio_inputs(input_fields)
            # self.handle_fieldset_radio_inputs(dialog)
            self.handle_select_fields(dialog)


            continue_btn = self.continueButton()

            if continue_btn:
                continue_btn.click()
            else:
                review_button = self.find_review_button()
                if review_button:
                    review_button.click()
                    break

        time.sleep(random.uniform(1, constants.botSpeed))
        
        self.handle_follow_company()
        time.sleep(random.uniform(1, constants.botSpeed))

        submit_btn = self.submitButton()
        if submit_btn:
            submit_btn.click()

        return "* 🥳 Just Applied to this job: " + str(offerPage)

    def displayWriteResults(self,lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("❌ Error in DisplayWriteResults: " +str(e))


if __name__ == "__main__":
    start = time.time()

    parser = argparse.ArgumentParser(
        prog='LinkedIn Job Application Bot',
        description='Automatically apply to LinkedIn jobs based on your criteria',
        epilog='For more information, visit: https://github.com/yourusername/EasyApplyJobsBot')

    parser.add_argument('--email', '-e', dest='email', help='LinkedIn email (optional, defaults to config.py)', default=config.email)
    parser.add_argument('--password', '-p', dest='password', help='LinkedIn password (optional, defaults to config.py)', default=config.password)
    parser.add_argument('--jobID', '-j', dest='jobID', help='Specific job ID to apply to', default=-1)
    parser.add_argument('--with_head', '-w', dest='with_head', help='Run browser in visible mode (not headless)', action='store_true')

    args = parser.parse_args()
    
    # Validate credentials
    if not args.email or not args.password:
        prRed("❌ Email and password must be provided either in config.py or as command line arguments")
        sys.exit(1)
        
    Linkedin(email=args.email, password=args.password, jobID=args.jobID, headless=not args.with_head).linkJobApply()
    end = time.time()
    prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
