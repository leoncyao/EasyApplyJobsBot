import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import utils
from utils import prRed, prYellow
import constants


class BrowserManager:
    def __init__(self, email, password, headless=True):
        self.email = email
        self.password = password
        self.driver = self.setup_driver(headless)
        self.login()

    def setup_driver(self, headless):
        """Setup Chrome driver with appropriate options"""
        prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
        chrome_options = utils.chromeBrowserOptions()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add these lines to disable GPU and WebGL warnings
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        return driver

    def login(self):
        """Login to LinkedIn"""
        prYellow("🔄 Trying to log in Linkedin...")
        try:    
            time.sleep(random.uniform(0.1, constants.botSpeed))
            self.driver.find_element("id","username").send_keys(self.email)
            time.sleep(random.uniform(0.1, constants.botSpeed))
            self.driver.find_element("id","password").send_keys(self.password)
            time.sleep(random.uniform(0.1, constants.botSpeed))
            self.driver.find_element("xpath",'//button[@type="submit"]').click()
            time.sleep(random.uniform(0.1, constants.botSpeed * 2))

            time.sleep(10)
        except Exception as e:
            prRed(e)
            prRed("❌ Couldn't log in Linkedin. Please check your credentials.")
            raise

    def close(self):
        """Close the browser"""
        self.driver.quit()

    def get_driver(self):
        """Get the WebDriver instance"""
        return self.driver 