# Project Locator

Crawler for new projects for software engineers.

## Launch

Run locally:
`python main.py`

Run in Docker:

`docker build . -t gulp-parser && docker run -it -e AWS_ACCESS_KEY_ID=<> -e AWS_SECRET_ACCESS_KEY=<> -e AWS_DEFAULT_REGION=<> gulp-parser`

See the dockerfile for more details.

Environment variables to set up:

`AWS_ACCESS_KEY_ID`

`AWS_SECRET_ACCESS_KEY`

`AWS_DEFAULT_REGION`


