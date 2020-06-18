import platform
import time

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# pick chromedriver based on OS
if platform.system() == 'Windows':
    chromedriver_path = 'chromedriver.exe'
elif platform.system() == 'Linux':
    chromedriver_path = 'chromedriver'

# comment out these options if you want to watch your chromedriver
# in action. These options including headless mode are used when we
# ship to production, run on a server with no gui, Docker, etc.
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

class Synthetic():
    '''
    synthetic includes methods needed for navigating around the airpa.io web pages 
    '''
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.wait = WebDriverWait(self.driver, 20)

    def goto_url(self, url):
        self.driver.get(url)
    
    def enter_text(self, text, xpath):
        elem = self.driver.find_element_by_xpath(xpath)
        elem.clear()
        elem.send_keys(str(text))            
    
    def click_action(self, xpath):
        elem = self.driver.find_element_by_xpath(xpath)
        elem.click()
    
    def wait_until_element_loads(self, xpath):
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))

    def wait_until_page_loads(self, parent_class):
        self.wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, parent_class)))
    
    def close(self):
        self.driver.quit()
    

class SyntheticCollector(object):
    '''
    SyntheticCollector utilizes the prometheus_client to collect and export metrics
    '''
    def __init__(self):
        self.ui = Synthetic()

    def collect(self):
        pass

