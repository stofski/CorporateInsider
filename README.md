# Corporate Insider

## Setup

1. Get an ec2 instance
2. Set up a cron job to git pull.
3. Install required deps.
4. Run `uvicorn app:app --reload --host 0.0.0.0 &` to start the back end.
5. Run `sudo python3 -m http.server 80 &`

If the cron job is set up correctly, it will poll for updates from bitbucket/github/etc, and the two commands to start the backend and the frontend willl watch for changes and automatically update the content and processes accordingly.

## dependencies

- python >3.8
  - uvicorn
  - fastapi
  - pydantic
  - boto3
