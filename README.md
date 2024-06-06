# Corporate Insider

## Setup

1. Get an ec2 instance
1. Set up secrets for OpenAI
1. Set up IAM Role with permission for Bedrock and Secrets
1. Attach IAM Role to the EC2 instance
1. In EC2: set up a cron job to git pull. (Continuous Deployment)
1. Install required deps .
1. Run `uvicorn app:app --reload --host 0.0.0.0 &` to start the back end.
1. Run `sudo python3 -m http.server 80 &` to start the front end.

If the cron job is set up correctly, it will poll for updates from bitbucket/github/etc, and the two commands to start the backend and the frontend willl watch for changes and automatically update the content and processes accordingly.

The commands may fail occasionally. They may need to be restarted. Another command or a service may need to be created for any long term deployment.

## dependencies

- python >3.8
  - uvicorn
  - fastapi
  - pydantic
  - boto3
  - langchain
  - langchain-community langchainhub langchain-openai langchain-chroma bs4
