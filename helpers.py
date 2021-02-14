from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import os


CHROME_LINUX_PATH = '/usr/local/bin/chromedriver'


def create_driver(is_headless):
    if is_headless:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
    else:
        chrome_options = None

    chrome_path = CHROME_LINUX_PATH
    env_var_path = os.environ.get('CHROME_PATH')
    if env_var_path:
        chrome_path = env_var_path

    return webdriver.Chrome(executable_path=chrome_path, options=chrome_options)  # Optional argument, if not specified will search path.


def find(driver, query, search_method=By.XPATH, wait=True):
    print("searching for element", query)
    if wait:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((search_method, query)))
    else:
        res = driver.find_elements(search_method, query)
        if len(res) == 0:
            return None
        else:
            return res[0]


def find_objects(driver, query, search_method=By.XPATH, wait=True):
    print("searching for element", query)
    if wait:
        return WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((search_method, query)))
    else:
        return driver.find_elements(search_method, query)


def open_new_tab(driver, url):
    driver.execute_script(f"window.open('{url}', '_blank');");
    driver.switch_to.window(driver.window_handles[-1])


def close_tab(driver):
    driver.execute_script("window.close();")
    driver.switch_to.window(driver.window_handles[-1])


def get_link_url(link):
    return link.get_attribute("href")
