from selenium.webdriver.common.by import By

from datetime import datetime

import helpers

URL = 'https://gulp.de/'

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
        "Auslastung": "load",
        "Projektanbieter": "project_provider",
        "Remote": "remote",
        "Stundensatz": "rate",
        "Skills": "skills"
    }


def find_projects(search_query, is_headless):
    print(f"Searching for projects in GULP with search_query='{search_query}' (headless={is_headless})...")
    driver = helpers.create_driver(is_headless)

    driver.get(URL)
    helpers.find(driver, 'onetrust-accept-btn-handler', By.ID)\
        .click()
    helpers.find(driver, "//*[@id='content']/div[1]/div[1]/div[2]/form/div[1]/input[2]") \
        .send_keys(search_query)
    helpers.find(driver, "//*[@id='content']/div[1]/div[1]/div[2]/form/div[2]/button") \
        .click()

    page = 1
    found_projects = []
    while True:
        print(f"Parsing page {page}...")
        viewed_links = []
        project_links_path = "//app-project-view/div/div/div[2]/h2/a"
        project_links = helpers.find_objects(driver, project_links_path)

        while len(project_links) > len(viewed_links):
            print(f"DEBUG: project_links={len(project_links)}, viewed={len(viewed_links)}, page={page}")
            print("searching for not viewed project...")
            current_link = None
            for link in project_links:
                if link.get_attribute("href") not in viewed_links:
                    current_link = link
                    break
            if not current_link:
                print("ERROR: cannot find not viewed project!")

            project_title = current_link.text
            print("Grabbing project '%s'" % project_title)
            viewed_links.append(current_link.get_attribute("href"))
            # go to the project page
            current_link.click()
            parsed_project = grab_project_safe(driver, project_title, search_query)
            if parsed_project:
                found_projects.append(parsed_project)
            else:
                print("Skipping project because of an error")

            # go back in history
            driver.execute_script("window.history.go(-1)")
            project_links = helpers.find_objects(driver, project_links_path)

        next_button = helpers.find(driver, "//a[@class='next']", By.XPATH, False)
        if next_button and next_button.find_element(By.XPATH, "..").get_attribute("class") != "disabled":
            page += 1
            print("waiting page %d to open..." % page)
            next_button.click()
            helpers.find(driver, build_page_link_path(page))
            print("next page is obtained!")
        else:
            break

    driver.quit()
    return found_projects


def grab_project_safe(driver, title, search_query):
    try:
        return grab_project(driver, title, search_query)
    except Exception as ex:
        print(f"ERROR: could not parse project {title}: {ex}")
        return None


def grab_project(driver, title, search_query):
    project = {}
    fields = helpers.find_objects(driver, "//app-display-readonly-value")
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

    description = helpers.find(driver, "//app-display-readonly-value[@class='gp-project-description']/div/div[2]", By.XPATH,
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
                                 helpers.find_objects(driver, "//app-readonly-tags-selection/div/div[2]/div/div",
                                              By.XPATH, False)))

    return project


def build_page_link_path(page_number):
    return "//app-paginated-list[@class='ng-star-inserted']/app-paginator/div/div/ul/div/li[*][" \
           "@class='ng-star-inserted active']/a[text()=%d]" % page_number
