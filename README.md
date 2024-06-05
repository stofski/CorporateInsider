# Corporate Insider

## Setup

1. On an ec2, set up a cron job to git pull.
2. Install required deps.
3. Run `uvicorn app:app --reload --host 0.0.0.0 &` to start the back end.
4. Run `sudo python3 -m http.server 80`

If the cron job is set up correctly, it will poll for updates from bitbucket/github/etc, and the two commands to start the backend and the frontend willl watch for changes and automatically update the content and processes accordingly.
