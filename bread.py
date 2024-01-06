from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Specify the path to the user profile directory

# Add the user profile directory to ChromeOptions

# Initialize the Chrome driver with ChromeOptions
# driver = webdriver.Chrome(options=options)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

chrome_profile_path = "C:\\Users\\leony\\AppData\\Local\\Google\\Chrome\\User Data\\"
# Replace 'path/to/chrome/profile' with the actual path to your Chrome user profile

# Specify the path to the user profile directory
# Replace 'path/to/chrome/profile' with the actual path to your Chrome user profile

# Create a ChromeOptions object

# Add the user profile directory to ChromeOptions

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# Example usage: Open a website

# Perform your automation tasks here

input()

# Close the browser
# driver.quit()
