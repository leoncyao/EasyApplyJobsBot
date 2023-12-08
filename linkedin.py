import time,math,random,os
import utils,constants,config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils import prRed,prYellow,prGreen

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains



class Linkedin:
    def __init__(self):
            prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
            chrome_options = utils.chromeBrowserOptions()
            # chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
            # self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=utils.chromeBrowserOptions())
            self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")

            prYellow("🔄 Trying to log in Linkedin...")
            try:    
                self.driver.find_element("id","username").send_keys(config.email)
                time.sleep(2)
                self.driver.find_element("id","password").send_keys(config.password)
                time.sleep(2)
                self.driver.find_element("xpath",'//button[@type="submit"]').click()
                time.sleep(20)
                self.linkJobApply()
            except:
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

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:        

            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH,'//small').text 
            totalPages = utils.jobsToPages(totalJobs)

            urlWords =  utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + urlWords[0] + ", Location: " +urlWords[1] + ", Applying " +str(totalJobs)+ " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url +"&start="+ str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [(offer.get_attribute(
                    "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
                time.sleep(random.uniform(1, constants.botSpeed))

                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    # offerPage = "https://www.linkedin.com/jobs/view/3766033127"
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1

                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties: 
                        lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " +str(offerPage)
                        self.displayWriteResults(lineToWrite)
                    
                    else :                    
                        easyApplybutton = self.easyApplyButton()

                        if easyApplybutton is not False:
                            easyApplybutton.click()
                            time.sleep(random.uniform(1, constants.botSpeed))
                            countApplied += 1
                            try:
                                self.chooseResume()
                                self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                                time.sleep(random.uniform(1, constants.botSpeed))

                                lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: "  +str(offerPage)
                                self.displayWriteResults(lineToWrite)

                            except:
                                try:
                                    self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
                                    time.sleep(random.uniform(1, constants.botSpeed))
                                    self.chooseResume()
                                    comPercentage = self.driver.find_element(By.XPATH,'html/body/div[3]/div/div/div[2]/div/div/span').text
                                    percenNumber = int(comPercentage[0:comPercentage.index("%")])
                                    result = self.applyProcess(percenNumber,offerPage)
                                    lineToWrite = jobProperties + " | " + result
                                    self.displayWriteResults(lineToWrite)
                                
                                except Exception as e: 
                                    print(f"exception + {str(e)}")
                                    self.chooseResume()
                                    lineToWrite = jobProperties + " | " + "* 🥵 Cannot apply to this Job! " +str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                                    g = open('data/url_fail_cases.txt', 'a')
                                    g.write("\n" + str(offerPage) + '\n')
                        else:
                            lineToWrite = jobProperties + " | " + "* 🥳 Already applied! Job: " +str(offerPage)
                            self.displayWriteResults(lineToWrite)


            prYellow("Category: " + urlWords[0] + "," +urlWords[1]+ " applied: " + str(countApplied) +
                  " jobs out of " + str(countJobs) + ".")
        
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

    def continueButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
            EasyApplyButton = button
        except: 
            EasyApplyButton = False

        return EasyApplyButton
    def applyProcess(self, percentage, offerPage):
        # applyPages = math.floor(100 / percentage) - 2 
        applyPages = math.floor(100 / percentage) 
        # /html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/div[2]/div/div/div[1]/div/input
        result = ""

        while self.continueButton():
            self.continueButton().click()
            # asdf = self.driver.find_elements_by_tag_name("input")
            # artdeco-modal-outlet
            # dialog = self.driver.find_element(By.ID, "artdeco-modal-outlet")
            # dialog = self.driver.find_element(By.CSS_SELECTOR, "div[aria-labelledby='jobs-apply-header']")
            dialog = self.driver.find_element(By.CLASS_NAME, "jobs-easy-apply-content")
            # print("id is " + dialog.get_attribute('id'))
            # print("inner_HTML is " + dialog.get_attribute('innerHTML'))
            input_fields = dialog.find_elements(By.TAG_NAME, "input")
            radio_fields = []
            for input_field in input_fields:
                if input_field.get_attribute("type") == "text":
                    input_field.send_keys("1")   
                elif input_field.get_attribute("type") == "radio":
                    if "Y" in input_field.get_attribute("value") or "y" in input_field.get_attribute("value"):
                        radio_fields.append(input_field)
            for radio_field in radio_fields:
                ActionChains(self.driver).click(radio_field).perform()
            # for input_field in input_fields:       
            #     time.sleep(random.uniform(1, constants.botSpeed))
            #     print("type of input is " + input_field.get_attribute("type"))
            #     if input_field.get_attribute("type") == "text":
            #         input_field.send_keys("1")   
            #     elif input_field.get_attribute("type") == "radio":
            #         print(input_field.get_attribute("value"))
            #         if "Y" in input_field.get_attribute("value") or "y" in input_field.get_attribute("value"):
            #             # input_field.click()
            #             ActionChains(self.driver).click(input_field).perform()
                        # self.driver.execute_script("arguments[0].checked = !arguments[0].checked;", input_field)
            select_fields = dialog.find_elements(By.TAG_NAME, "select")
            for select_field in select_fields:
                Select(select_field).select_by_index(1)
            # for input_field in input_fields:       
            #     time.sleep(random.uniform(1, constants.botSpeed))
            #     input_field.send_keys("1")   
                                                                
            # username_input_field = self.driver.find_element("id", "userNameInput")
            # username_input_field.send_keys("lclyao@uwaterloo.ca")
            


        self.driver.find_element( By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        if config.followCompanies is False:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
            except:
                pass

        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "* 🥳 Just Applied to this job: " + str(offerPage)

        return result

    def displayWriteResults(self,lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("❌ Error in DisplayWriteResults: " +str(e))

start = time.time()
Linkedin().linkJobApply()
end = time.time()
prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
