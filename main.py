import sys

import dynamodb
import gulp_grabber
import freelance_grabber

HEADLESS = True

def info_print(projects):
    print("\nRESULTS:")
    for project in projects:
        print(project["title"])
        for key, value in project.items():
            if key != "title":
                print("  %s: %s" % (key, value))

    print("Total %d projects!" % len(projects))


if __name__ == '__main__':
    print("==============================")
    source = "gulp"
    query = "golang"
    if len(sys.argv) != 3:
        print("WARNING: not enough arguments. Two arguments needed: arg1=[gulp|freelance_de], arg2=[java|devops|...]")
        print("Using testing arguments...")
    else:
        source = sys.argv[1]
        query = sys.argv[2]

    projects = []
    if source == 'gulp':
        projects = gulp_grabber.find_projects(query, HEADLESS)
    elif source == 'freelance_de':
        projects = freelance_grabber.find_projects(query, HEADLESS)
    else:
        print("ERROR: source is unknown:", source)

    info_print(projects)
    added = 0
    print("Saving the results into the database...")
    for project in projects:
        added_project = dynamodb.create_project_if_not_exists(project)
        #added_project = None
        if added_project:
            added += 1

    print(f"By query '{query}' found {len(projects)} projects. Added to database: {added}")

