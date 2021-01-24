import boto3
import uuid
import calendar
import time
from boto3.dynamodb.conditions import Key

PROJECTS_TABLE = 'pl_projects'

def create_project(project):
    print("DynamoDB: saving project:", project['title'])
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(PROJECTS_TABLE)
    project['id'] = str(uuid.uuid4())
    project['createdAt'] = calendar.timegm(time.gmtime())   # utc timestamp in sec
    response = table.put_item(Item=project)
    print(response)


def create_project_if_not_exists(project):
    existing_project = find_project_by_url(project['url'])
    if existing_project:
        print(f"project with URL {project['url']} already in the database")
        return None
    else:
        create_project(project)
        print(f"project saved! (URL: {project['url']})")


def find_project_by_url(url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(PROJECTS_TABLE)

    response = table.query(
        IndexName='url-index',
        KeyConditionExpression=Key('url').eq(url)
    )
    if len(response['Items']) > 0:
        return response['Items'][0]
    else:
        return None
