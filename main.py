from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import dynamodb

URL = 'https://gulp.de/'
CHROME_PATH = '/usr/local/bin/chromedriver'
FIELD_MAP = {
        "publication_time": "Veröffentlicht am",
        "location": "Einsatzort",
        "gulp_job_id": "Job-ID",
        "start": "Beginn",
        "duration": "Dauer",
        "description": "Beschreibung"
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
                found_projects.append(grab_project(driver, project_title))
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


def grab_project(driver, title):
    project = {}
    fields = find_objects(driver, "//app-display-readonly-value")
    parsed = {}
    for field in fields:
        splited = field.text.split("\n")
        if len(splited) == 2:
            parsed[splited[0]] = splited[1]

    project["title"] = title
    project["source"] = "gulp"
    project["url"] = driver.current_url
    assign_field(project, parsed, "publication_time")
    assign_field(project, parsed, "location")
    assign_field(project, parsed, "gulp_job_id")
    assign_field(project, parsed, "start")
    assign_field(project, parsed, "duration")
    assign_field(project, parsed, "description")

    project["description"] = find(driver, "//app-display-readonly-value[@class='gp-project-description']/div/div[2]").text
    project["skills"] = list(map(lambda x: x.text,
                                 find_objects(driver, "//app-readonly-tags-selection/div/div[2]/div/div")))

    return project


def assign_field(result_dict, parsed_input, field_name):
    mapped_name = FIELD_MAP[field_name]
    parsed_value = parsed_input.get(mapped_name)
    if parsed_value:
        result_dict[field_name] = parsed_value


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


def find_objects(driver, query, search_method=By.XPATH):
    print("searching for element", query)
    return WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((search_method, query)))


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
    for project in projects:
        dynamodb.create_project(project)

    print("All the new projects are added!")

