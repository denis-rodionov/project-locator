from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


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