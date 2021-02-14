from typing import Dict, List, Any, Union

import helpers
import time
import os
from selenium.webdriver.common.by import By

URL = "https://www.freelance.de/search/project.php"
FIELD_MAP = {
    "Geplanter Start": "start",
    "Projektort": "location",
    "Stundensatz": "rate",
    "Letztes Update": "publication_time",
    "Voraussichtliches Ende": "end"
}

def find_projects(search_query, is_headless):
    print(f"Searching for projects in Freelance.de with search_query={search_query}...")
    driver = helpers.create_driver(is_headless)


    # login
    username = os.environ.get("FREELANCE_DE_USER")
    password = os.environ.get("FREELANCE_DE_PASSWORD")
    if not username or not password:
        raise Exception("ERROR: one of the env the variables are missing: FREELANCE_DE_USER and FREELANCE_DE_PASSWORD")
    login(driver, username, password)

    driver.get(URL)

    # search by the given query
    helpers.find(driver, "//*[@id='__search_freetext']").send_keys(search_query)
    helpers.find(driver, "//*[@id='search_simple']").click()

    # sort by date
    helpers.find(driver, "//button[@data-id='__search_sort_by_remote']").click()
    helpers.find(driver, "//span/div/div/ul/li[2]/a").click()

    # parsing project links
    links = helpers.find_objects(driver, "//div[@class='freelancer-content']/h3/a")

    projects = []
    link_num = 0
    for link in links:
        link_num += 1
        print(f"Parsing project #{link_num}...")
        helpers.open_new_tab(driver, helpers.get_link_url(link))

        projects.append(parse_project(driver, search_query))
        helpers.close_tab(driver)

    return projects


def parse_project(driver, search_query):
    project = {}

    # default fields
    project["source"] = "freelance_de"
    project["url"] = driver.current_url
    project["search_query"] = search_query

    # project title
    project['title'] = helpers.find(driver, "//div[@class='panel-body project-header panel-white']/h1").text

    # details
    parse_project_details(driver, project)

    # description
    project['description'] = helpers.find_objects(
        driver, "//div[@class='panel panel-default panel-white']")[0].text
    
    # skills
    skills_elements = helpers.find_objects(driver, "//div/ul/li[*]/ul/li[*]/a", By.XPATH, False)
    project['skills'] = list(map(lambda x: x.text, skills_elements))

    return project


def parse_project_details(driver, project):
    fields = helpers.find_objects(driver, "//div[@class='project-right-content']//p")
    for field in fields:
        title_elements = helpers.find_objects(field, "i", By.TAG_NAME, False)
        if not title_elements:
            continue
        title = title_elements[0].get_attribute("data-original-title")

        if title == "Remote-Einsatz möglich":
            project["location"] = project["location"] + " (Remote)"
            continue

        domain_field_name = FIELD_MAP.get(title)
        if not domain_field_name:
            print(f"WARNING: unknown field '{title}'")
        project[domain_field_name] = field.text


def login(driver, username, password):
    driver.get("https://www.freelance.de/login.php")

    # agree to compliance policy
    helpers.find(driver, "//a[@class='cc-btn cc-dismiss']").click()

    helpers.find(driver, "//input[@id='username']").send_keys(username)
    helpers.find(driver, "//input[@id='password']").send_keys(password)
    helpers.find(driver, "//input[@id='login']").click()
    time.sleep(2)