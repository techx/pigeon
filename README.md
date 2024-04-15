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
├── .devcontainer                 # Dev container configuration
├── README.md
├── requirements.txt              # Python dependencies list for backend
├── .env                          # Stores secrets that are not in VCS
├── wsgi.py                       # Flask entry point
├── scripts
│   ├── deploy.sh                 # Deploy to production server
│   └── devcontainer_setup.sh     # Run once when the dev container initializes
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

Copy `.env.sample` to `.env` and fill in the necessary values. You should be able to find them on slack.

## Docker

Using [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-an-existing-folder-in-a-container) are strongly recommended when doing development work on pigeon. Containers are a way of provisioning identical environments from computer to computer and alleviates a lot of headache when it comes to installing dependencies, setting up Postgres, etc...

To use Dev Containers you must first install [Visual Studio Code](https://code.visualstudio.com/) and [Docker](https://www.docker.com/get-started/). Then you must install the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for Visual Studio Code.

To use Docker, install it [here](https://docs.docker.com/get-docker/). To check if your installation is working, try running

```sh
docker run hello-world
```

If you get a message on your screen that starts with "Hello from Docker!", your installation is working.

After that, follow [this tutorial](https://www.youtube.com/watch?v=Uvf2FVS1F8k) to get your environment set up. Make sure you open this repository as a dev container in VSCode.

> Note: It can take a few minutes to provision the container if it is your first time starting it up.

## Development

To start the server, run

```sh
python3 run.py
```

To start the client, in a different terminal, run
```sh
cd client
npm run dev
```

The postgres and redis services are running on the same network as the dev container, but they can only communicate with each other via the designated service names, which are `database` and `redis` respectively. If you want to view these services from inside the dev container, you can use the following commands:

```sh
# postgres
PGPASSWORD='password' psql -h database -U postgres

# redis
redis-cli -h redis
```

Check redis keys with
```sh
keys *
```

Alternatively, you can access these services from your local machine, i.e., outside of the dev container, by connecting directly to the docker containers. To do this, run

```sh
docker container ls
```

and retrieve the container id of your desired instance (e.g., `pigeon_devcontainer-database-1`). Then, run

```sh
docker exec -it <container_id> /bin/bash
```

to enter the container, from which you should be able to run `psql` or `redis-cli` directly.

### Installing Python Dependencies

Put all direct dependencies (i.e., packages we directly import) in `requirements.in`. pigar can be used to automate part of this process. Then, run
```
pip-compile
```
to generate requirements.txt, which contains pinned versions of subdependencies as well.

### AWS

All emails are forwarded to Pigeon through [AWS](https://aws.amazon.com/). More specifically, emails are received with a [receipt rule](https://docs.aws.amazon.com/ses/latest/dg/receiving-email-concepts.html) and forwarded to an [S3 bucket](https://aws.amazon.com/s3/), which are then processed and forwarded to the api with a [lambda](https://aws.amazon.com/lambda/). The receiving and sending rules are both handled by [SES](https://aws.amazon.com/ses/).

For instructions on setting up locally, see [go/pigeon-aws](https://docs.google.com/document/d/1ASPwrC0LeI1jgSu9yML05zhb3SXFs6xe-xUKox3JWNw/edit).
