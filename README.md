# Itol Task Manager

## Setup and run

### Install dependencies

Install and activate venv then:

```sh
pip install -r requirements.txt
```

### Initialize DB

#### Set environment variable

Powershell:
```ps1
$Env:FLASK_APP = "src.web.app:create_app"
```
Bash:
```sh
export FLASK_APP="src.web.app:create_app"
```

#### Run init command

```sh
flask init-db
```

### Run

```sh
python3 .\src\main.py
```
