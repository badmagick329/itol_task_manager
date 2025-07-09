# Itol Task Manager

## Overview

A CRUD app + auth demo using flask

## How to run

Make sure you create a `.env` file based on `.env.sample`.

### Local setup and run

#### Install dependencies

Install and activate venv then:

```sh
pip3 install -r requirements.txt
```

#### Initialize DB

##### Set environment variable

Powershell:

```ps1
$Env:FLASK_APP = "src.web.app:create_app"
```

Bash:

```sh
export FLASK_APP="src.web.app:create_app"
```

##### Run init command

```sh
flask init-db
```

#### Run

```sh
python3 .\src\main.py
```

The app will be accessible on `http://<your_local_ip or localhost>:<your_chosen_port>`

### Docker

```sh
docker-compose up -d
# To init db or to apply any changes:
docker-compose exec web flask int-db
```

The app will be accessible on `http://<your_public_ip or domain>:<your_chosen_port>`

## How to test

Make sure you've installed the dependencies from `requirements.txt`

```sh
python3 -m pytest
```

## List of additional features

- Task Export - Tasks can be exported as csv using python's csv module
- Search - Search is performed on the backend based on search params, making it easy to copy paste the URL and retrieve the same results on another device or tab
- Task Sorting - Task sorting is handled on the frontend to avoid full page reloads
