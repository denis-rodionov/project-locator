import boto3
import uuid

def create_project(project):
    print("DynamoDB: saving project:", project['title'])
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pl_projects')
    project['id'] = str(uuid.uuid4())
    response = table.put_item(Item=project)
    print(response)