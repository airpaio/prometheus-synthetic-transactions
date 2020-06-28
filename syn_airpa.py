import platform
import time

from prometheus_client import start_http_server, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily

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

# unregister some default prometheus metrics that are not needed.
# these are metric on python runtime and garbage collection
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])

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
    

class SyntheticCollector():
    '''
    SyntheticCollector utilizes the prometheus_client to collect and export metrics
    '''

    def describe(self):
        return []

    def collect(self):
        '''
        collect is the method that defines the metrics and collects them to publish them
        at your /metrics endpoint that Prometheus will scrape from. 
        '''        
        metrics = {}
        metrics = {
            'landing_page': GaugeMetricFamily(
                'synthetic_time_to_landing_page',
                'The page load time for navigating to "https:airpa.io/login".',
                labels=["synthetic_app"]
            ),
            'login': GaugeMetricFamily(
                'synthetic_time_to_login',
                'The duration of page load time for logging into "https:airpa.io/login".',
                labels=["synthetic_app"]
            ),
            'logout': GaugeMetricFamily(
                'synthetic_time_to_logout',
                'The duration of page load time for logging out of "https:airpa.io".',
                labels=["synthetic_app"]
            )
        }

        # run the synthetic transaction to get the metrics
        print('Collecting synthetic metrics for "synthetic_app": "airpa"...')
        landing, login, logout = synthetic_run('username', 'password')
        print("Time to landing page: {}".format(landing))
        print("Time to login: {}".format(login))
        print("Time to logout: {}".format(logout))

        # add the metrics to the prometheus collector
        metrics['landing_page'].add_metric(labels=["airpa"], value=landing)
        metrics['login'].add_metric(labels=["airpa"], value=login)
        metrics['logout'].add_metric(labels=["airpa"], value=logout)

        for metric in metrics.values():
            yield metric
        
        print("Finished running collect().")
        

def synthetic_run(username, password):
    '''
    synthetic_run will step thru the ui actions, taking time metrics at specified points
    '''
    ui = Synthetic()
    start = time.time()
    ui.goto_url("https://airpa.io/login/") 
    ui.wait_until_page_loads("default")  # initial landing page load completed
    landing_page_load_time = time.time() - start

    start = time.time()
    ui.enter_text(username, '//*[@id="authcontainer"]/div[1]/input')
    ui.enter_text(password, '//*[@id="authcontainer"]/div[2]/input')
    ui.click_action('//*[@id="authcontainer"]/div[3]/button')
    ui.wait_until_element_loads('//*[@id="authenticator"]/div[1]/h2')  # login completed
    login_time = time.time() - start

    start = time.time()
    ui.click_action('//*[@id="menuIcon"]/div')
    ui.wait_until_element_loads('//*[@id="signoutButton"]')
    ui.click_action('//*[@id="signoutButton"]')
    ui.wait_until_page_loads("default")  # logout completed
    logout_time = time.time() - start
    ui.close()

    return landing_page_load_time, login_time, logout_time

if __name__ == "__main__":
    start_http_server(port=9901)
    print('Listening on localhost:9901')
    print('Metrics will be scraped from http://127.0.0.1:9901/synthetic-metrics')
    REGISTRY.register(SyntheticCollector())    
    while True:
        time.sleep(1)
