import time, random
import utils, constants, config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from utils import prRed, prYellow, prGreen

class JobApplier:
    def __init__(self, driver, job_url=None, headless=True):
        self.driver = driver
        self.job_url = job_url

    def apply_to_job(self, job_url):
        """Main method to apply to a specific job"""

        self.driver.get(job_url)
        time.sleep(2)

        easy_apply_button = self.easy_apply_button()
        if not easy_apply_button:
            prYellow(f"🥳 Already applied! Job: {job_url}")
            return False

        try:
            easy_apply_button.click()
            time.sleep(2)
            
            if self._complete_application_process():
                prGreen(f"✅ Successfully applied to: {job_url}")
                return True
            else:
                prRed(f"❌ Failed to apply to: {job_url}")
                return False
                
        except Exception as e:
            prRed(f"Error during application process: {str(e)}")
            return False

    def get_job_properties(self):
        """Get job details and properties"""
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
            time.sleep(random.uniform(0.1, constants.botSpeed * 5))
            jobDetail = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                prYellow("⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text
        except Exception as e:
            if (config.displayWarnings):
                prYellow("⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        return f"1 | {jobTitle} | {jobDetail}{jobLocation}"

    def _handle_blacklisted_job(self, job_properties):
        """Handle blacklisted job cases"""
        line_to_write = f"{job_properties} | * 🤬 Blacklisted Job, skipped!: {self.job_url}"
        self.display_write_results(line_to_write)

    def _handle_job_application(self, job_properties):
        """Handle the job application process"""
        easy_apply_button = self.easy_apply_button()
        
        if not easy_apply_button:
            line_to_write = f"{job_properties} | * 🥳 Already applied! Job: {self.job_url}"
            self.display_write_results(line_to_write)
            return False

        try:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            easy_apply_button.click()
            time.sleep(random.uniform(0.1, constants.botSpeed))
            
            if self._complete_application_process():
                return True
            else:
                self._handle_failed_application(job_properties)
                return False
                
        except Exception as e:
            prRed(f"Error during application process: {str(e)}")
            return False

    def _complete_application_process(self):
        """Complete the multi-step application process"""
        max_attempts = 10
        attempt = 0
        # once for autofilled data
        continue_btn = self.continue_button()
        if continue_btn:
            continue_btn.click()
        time.sleep(random.uniform(0.1, constants.botSpeed))
        # self.choose_resume()
        # once for resume (which should already be uploaded)
        continue_btn = self.continue_button()
        if continue_btn:
            continue_btn.click()

        while attempt < max_attempts:
            try:

                self.apply_process()
                time.sleep(random.uniform(0.1, constants.botSpeed))
                
                continue_btn = self.continue_button()

                if continue_btn:
                    continue_btn.click()
                else:
                    review_button = self.find_review_button()
                    if review_button:
                        review_button.click()
                        break

                attempt += 1
            except Exception as e:
                print(f"Error in application step: {e}")
                break

        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
            time.sleep(random.uniform(0.1, constants.botSpeed))
            submit_button.click()
            return True
        except:
            return False

    def _handle_failed_application(self, job_properties):
        """Handle failed application cases"""
        line_to_write = f"{job_properties} | * 🥵 Cannot apply to this Job! {self.job_url}"
        self.display_write_results(line_to_write)
        with open('data/url_fail_cases.txt', 'a') as g:
            g.write(f"\n{self.job_url}\n")

    def easy_apply_button(self):
        """Find and return the Easy Apply button"""
        try:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            button = self.driver.find_element(By.XPATH, "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]")
            return button
        except: 
            return False

    def submitButton(self):
        try:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
            SubmitButton = button
        except: 
            SubmitButton = False

        return SubmitButton

    def find_review_button(self):
        try:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            review_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']")
            return review_button
        except: 
            return False

    def choose_resume(self):
        """Handle resume selection"""
        try:
            self.driver.find_element(By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                time.sleep(random.uniform(0.1, constants.botSpeed))
                resumes[0].click()
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                time.sleep(random.uniform(0.1, constants.botSpeed))
                resumes[config.preferredCv-1].click()
            elif (type(len(resumes)) != int):
                prRed("❌ No resume has been selected please add at least one resume to your Linkedin account.")

            time.sleep(random.uniform(0.1, constants.botSpeed))
            self.continue_button().click()
        except:
            pass

    def continue_button(self):
        """Find and return the Continue button"""
        try:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
            return button
        except: 
            return False

    def apply_process(self):
        """Main process for handling job application form"""
        time.sleep(random.uniform(0.1, constants.botSpeed * 2))

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
        # self.handle_radio_inputs(input_fields)
        self.handle_fieldset(dialog)
        self.handle_select_fields(dialog)




    def handle_text_inputs(self, input_fields):
        """Handle text input fields"""
        for input_field in input_fields:
            if input_field.get_attribute("type") == "text":
                if "city" in input_field.get_attribute("id").lower():
                    self._handle_city_input(input_field)
                else:
                    self._handle_generic_text_input(input_field)

    def _handle_city_input(self, input_field):
        """Handle city input field"""
        time.sleep(random.uniform(0.1, constants.botSpeed))
        input_field.send_keys("Toronto")     
        time.sleep(random.uniform(0.1, constants.botSpeed))   
        input_field.send_keys(Keys.DOWN)        
        time.sleep(random.uniform(0.1, constants.botSpeed))       
        input_field.send_keys(Keys.ENTER) 

    def _handle_generic_text_input(self, input_field):
        """Handle generic text input"""
        if len(input_field.get_attribute("value")) == 0:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            input_field.send_keys("3")

    def handle_radio_inputs(self, input_fields):
        """Handle radio input fields"""
        for field in input_fields:
            print(f"Type: {field.get_attribute('type')}")
            try:
                parent = field.find_element(By.XPATH, "./..")
                print(f"Parent text: {parent.text}")
            except Exception as e:
                print(f"No child elements found: {str(e)}")
            print("---")
        
        radio_fields = [field for field in input_fields if field.get_attribute("type") == "radio" 
                       and "y" in field.get_attribute("value").lower()]
        
        for radio_field in radio_fields:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            ActionChains(self.driver).click(radio_field).perform()
            time.sleep(random.uniform(0.1, constants.botSpeed))

    def handle_select_fields(self, dialog):
        """Handle select/dropdown fields"""
        select_fields = dialog.find_elements(By.TAG_NAME, "select")
        for select_field in select_fields:
            time.sleep(random.uniform(0.1, constants.botSpeed))
            Select(select_field).select_by_index(1)

    def handle_fieldset(self, dialog):
        """Handle radio inputs within fieldsets by selecting the first option"""
        fieldsets = dialog.find_elements(By.TAG_NAME, "fieldset")
        for i, fieldset in enumerate(fieldsets, 1):
            try:
                print(f"\nFieldset {i}:")
                # Find all radio inputs in this fieldset
                radio_inputs = fieldset.find_elements(By.TAG_NAME, "input")
                if radio_inputs:
                    print(f"Found {len(radio_inputs)} radio inputs:")
                    for j, radio in enumerate(radio_inputs, 1):
                        try:
                            # Try to get the label text
                            label = radio.find_element(By.XPATH, "./..").text
                            print(f"  Option {j}:")
                            print(f"    Label: {label}")
                            print(f"    Type: {radio.get_attribute('type')}")
                        except Exception as e:
                            print(f"  Option {j}: Could not get details - {str(e)}")
                    
                    # Get the first radio input
                    first_radio = radio_inputs[0]
                    if first_radio.get_attribute("type") == "radio" or first_radio.get_attribute("type") == "checkbox":
                        try:
                            first_label = first_radio.find_element(By.XPATH, "./..").text
                            print(f"\nSelecting first option in fieldset {i}:")
                            print(f"  Label: {first_label}")
                            print(f"  Type: {first_radio.get_attribute('type')}")
                            time.sleep(random.uniform(0.1, constants.botSpeed))
                            try:
                                ActionChains(self.driver).click(first_radio).perform()
                            except:
                                print("couldn't click first radio")
                            time.sleep(random.uniform(0.1, constants.botSpeed))
                        except Exception as e:
                            print(f"Could not get details of first option: {str(e)}")
                else:
                    print("No radio inputs found in this fieldset")
            except Exception as e:
                print(f"Error handling fieldset {i}: {str(e)}")
                continue

    def display_write_results(self, line_to_write):
        """Display and write results"""
        try:
            print(line_to_write)
            utils.writeResults(line_to_write)
        except Exception as e:
            prRed("❌ Error in DisplayWriteResults: " + str(e))

    def close(self):
        """Close the browser"""
        self.driver.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply to a specific LinkedIn job')
    parser.add_argument('--url', required=True, help='LinkedIn job URL to apply to')
    parser.add_argument('--email', default=config.email, help='LinkedIn email')
    parser.add_argument('--password', default=config.password, help='LinkedIn password')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    applier = JobApplier(email=args.email, password=args.password, job_url=args.url, headless=args.headless)
    try:
        applier.apply_to_job()
    finally:
        applier.close() 