from selenium.webdriver.common.by import By

self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()

button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")

button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")

dialog = self.driver.find_element(By.CLASS_NAME, "jobs-easy-apply-content")

dialog = self.driver.find_element(By.CSS_SELECTOR, "[data-test-modal-id='easy-apply-modal']")