from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime

import dynamodb

URL = 'https://gulp.de/'
CHROME_PATH = '/usr/local/bin/chromedriver'
FIELD_MAP = {
        "Veröffentlicht am": "publication_time",
        "Einsatzort": "location",
        "Job-ID": "gulp_job_id",
        "Beginn": "start",
        "Dauer": "duration",
        "Projekt-Beschreibung": "description",
        "Beschreibung": "description",
        "Titel": "title",
        "Projekt-Titel": "title",
        "Projekt-Rolle": "role",
        "Auslastung": "load"
    }


def find_projects(search_query, is_headless):
    if is_headless:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
    else:
        chrome_options = None


    driver = webdriver.Chrome(executable_path=CHROME_PATH, options=chrome_options)  # Optional argument, if not specified will search path.
    driver.get(URL)
    find(driver, 'onetrust-accept-btn-handler', By.ID)\
        .click()
    find(driver, "//*[@id='content']/div[1]/div[1]/div[2]/form/div[1]/input[2]") \
        .send_keys(search_query)
    find(driver, "//*[@id='content']/div[1]/div[1]/div[2]/form/div[2]/button") \
        .click()

    page = 1
    found_projects = []
    while True:
        viewed_links = []
        project_links_path = "//app-project-view/div/div/div[2]/h2/a"
        project_links = find_objects(driver, project_links_path)

        index = 0
        while len(project_links) > len(viewed_links):
            link = project_links[index]
            index += 1
            if link.text in viewed_links:
                continue
            else:
                project_title = link.text
                print("Grabbing project '%s'" % project_title)
                viewed_links.append(project_title)
                # go to the project page
                link.click()
                found_projects.append(grab_project(driver, project_title, search_query))
                # go back in history
                driver.execute_script("window.history.go(-1)")
                project_links = find_objects(driver, project_links_path)

        next_button = find(driver, "//a[@class='next']", By.XPATH, False)
        if next_button and next_button.find_element(By.XPATH, "..").get_attribute("class") != "disabled":
            page += 1
            print("waiting page %d to open..." % page)
            next_button.click()
            find(driver, build_page_link_path(page))
            print("next page is obtained!")
        else:
            break

    driver.quit()
    return found_projects


def grab_project(driver, title, search_query):
    project = {}
    fields = find_objects(driver, "//app-display-readonly-value")
    parsed = {}
    for field in fields:
        splited = field.text.split("\n")
        if len(splited) > 1:
            parsed[splited[0]] = "\n".join(splited[1:])

    project["source"] = "gulp"
    project["url"] = driver.current_url
    project["search_query"] = search_query

    for parsed_key, parsed_value in parsed.items():
        domain_property = FIELD_MAP.get(parsed_key)
        if domain_property:
            project[domain_property] = parsed_value
        else:
            print("UNKNOWN FIELD:", parsed_key)

    description = find(driver, "//app-display-readonly-value[@class='gp-project-description']/div/div[2]", By.XPATH,
                       False)
    if description:
        project["description"] = description.text

    if not project["title"]:
        project["title"] = title

    publication_time = project['publication_time']
    if publication_time:
        try:
            project['publication_timestamp'] = \
                int(datetime.strptime(publication_time, '%d.%m.%Y %H:%M h').timestamp())
        except Exception as err:
            print(f"ERROR: cannot parse publication date '{publication_time}': {err}")

    project["skills"] = list(map(lambda x: x.text,
                                 find_objects(driver, "//app-readonly-tags-selection/div/div[2]/div/div",
                                              By.XPATH, False)))

    return project


def build_page_link_path(page_number):
    return "//app-paginated-list[@class='ng-star-inserted']/app-paginator/div/div/ul/div/li[*][" \
           "@class='ng-star-inserted active']/a[text()=%d]" % page_number


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


def info_print(projects):
    print("\nRESULTS:")
    for project in projects:
        print(project["title"])
        for key, value in project.items():
            if key != "title":
                print("  %s: %s" % (key, value))

    print("Total %d projects!" % len(projects))


if __name__ == '__main__':
    projects = find_projects("golang", True)
    #info_print(projects)
    for project in projects:
        dynamodb.create_project_if_not_exists(project)

    print("All the new projects are added!")

