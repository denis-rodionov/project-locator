# Project Locator
![Deploy to Amazon ECS](https://github.com/denis-rodionov/project-locator-grabber/workflows/Deploy%20to%20Amazon%20ECS/badge.svg)

Crawler for new projects for software engineers.

## Run

Run locally:
`python main.py`

Run in Docker:

`docker build . -t gulp-parser && docker run -it -e AWS_ACCESS_KEY_ID=<> -e AWS_SECRET_ACCESS_KEY=<> -e AWS_DEFAULT_REGION=<> gulp-parser`

See the dockerfile for more details.

Environment variables to set up:

`AWS_ACCESS_KEY_ID`

`AWS_SECRET_ACCESS_KEY`

`AWS_DEFAULT_REGION`

## Deploy
The parser is supposed to be deployed on AWS ECS as a scheduled task. So the deployment consists of the steps:
1. Build the image
2. Push the image to ECR
3. Create ECS task definition based on the image
4. Deploy ECS task definition to the cluster as a scheduled task.

Automatic Deployment happens by GitHub Action. The definition is stored in .github/workflows/aws.yaml

Permissions for GitHub required (TODO: currently overprivileged, limit access):
* AmazonEC2ContainerRegistryFullAccess 
* AmazonElasticContainerRegistryPublicFullAccess 
* AmazonECS_FullAccess
* CloudWatchEventsReadOnlyAccess

Also, in order to grant iam::PassRole permission, need to create the corresponding policy: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html