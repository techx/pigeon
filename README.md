<h1 align="center">Pigeon</h1>

<div align="center">
	<a href="#overview">Overview</a>
  <span> • </span>
    	<a href="#setup">Setup</a>
  <span> • </span>
    	<a href="#development">Development</a>
  <p></p>
</div>

Pigeon is HackMIT's RAG email assistant. Pigeon helps automates the help email workflow.

## Overview

Pigeon uses [Flask](https://flask.palletsprojects.com/en/2.2.x/) for its backend framework and [React](https://reactjs.org) for its frontend framework. It is built on an in-memory [Redis](https://redis.io/) database that stores embedding data for documents and emails, along with [Postgres](https://www.postgresql.org/) for longer-term database management. The emailing service is automated with [AWS](https://aws.amazon.com/), see below for details.

### Directory Overview

```
pigeon/
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.redis
├── docker-compose.yml
├── README.md
├── requirements.txt
├── .env
├── wsgi.py
└── client
│   ├── public
│   │   └── pigeon.png
│   ├── src
│   │   ├── App.tsx
│   │   ├── main.css
│   │   ├── main.tsx
│   │   ├── routes
│   │   │   ├── documents.module.css
│   │   │   ├── documents.tsx
│   │   │   ├── inbox.module.css
│   │   │   ├── inbox.tsx
│   │   │   ├── index.module.css
│   │   │   └── index.tsx
│   │   ├── shell.tsx
│   │   └── vite-env.d.ts
└── server
    ├── config.py
    ├── controllers
    │   ├── admin.py
    │   ├── emails.py
    │   └── faq.py
    ├── email_template
    │   └── template.html
    ├── models
    │   ├── document.py
    │   ├── email.py
    │   ├── response.py
    │   └── thread.py
    └── nlp
        ├── corpus_harvard.json
        ├── corpus_mit.json
        ├── embeddings.json
        ├── embeddings.py
        └── responses.py
```

### Requirements

[Docker](https://docs.docker.com/get-started/). See setup instructions below.

## Setup

### Env

Fill in the `.env` file (should be able to find it on Slack).

```env
FRONTEND_URL=""
BACKEND_URL=""
BACKEND_URL_DOCKER=""
MAIL_USERNAME=""
MAIL_PASSWORD=""

AUTH_CLIENT_ID=""
AUTH_CLIENT_SECRET=""
AUTH_USERNAME=""
AUTH_PASSWORD=""

SESSION_SECRET=""

OPENAI_API_KEY=""

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = ""
```

### Docker

Docker is a way to provision identical environments from computer to computer and alleviates a lot of headache when it comes to installing dependencies, setting up postgres/redis, etc.

To use Docker, install it [here](https://docs.docker.com/get-docker/). To check if your installation is working, try running

```sh
docker run hello-world
```

If you get a message on your screen that starts with "Hello from Docker!", your installation is working.

To begin development, cd into your `/postgres` directory and run:

```sh
docker compose up
```

This command will install every React, Flask, Postgres, and Redis dependency you need to run Pigeon into containers that interact with each other separately from the rest of your machine. To know when Pigeon is ready to run, you should look for four messages:

```sh
pigeon-postgresdb-1  | ... database system is ready to accept connections
pigeon-redis-1       | ... Ready to accept connections tcp
pigeon-backend-1     | ... * Running on all addresses (0.0.0.0)
pigeon-frontend-1    | ... ready in 1486 ms
```

If it is your first time starting up Pigeon, it may take a while for all four of these messages to show up (on the order of tens of minutes). Once everything is running, navigate to `http://localhost:5173` to see Pigeon's homepage.

Once you are done, you can Ctrl+C or run

```sh
docker compose down
```

to close all open Pigeon containers.

## Development

### AWS

All emails are forwarded to Pigeon through [AWS](https://aws.amazon.com/). More specifically, emails are received with a [receipt rule](https://docs.aws.amazon.com/ses/latest/dg/receiving-email-concepts.html) and forwarded to an [S3 bucket](https://aws.amazon.com/s3/), which are then processed and forwarded to the api with a [lambda](https://aws.amazon.com/lambda/). The receiving and sending rules are both handled by [SES](https://aws.amazon.com/ses/). 

For instructions on setting up locally, see [go/pigeon-aws](https://docs.google.com/document/d/1ASPwrC0LeI1jgSu9yML05zhb3SXFs6xe-xUKox3JWNw/edit).
