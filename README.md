[![build](https://travis-ci.org/perewall/touchresume.svg?branch=master)](https://travis-ci.org/perewall/touchresume)
[![coverage](https://codecov.io/gh/perewall/touchresume/branch/master/graph/badge.svg)](https://codecov.io/gh/perewall/touchresume)
[![heroku](https://img.shields.io/badge/%E2%86%91_Deploy_to-Heroku-7056bf.svg)](https://heroku.com/deploy)


# TouchResume

Tool for automatically update your CV on some job boards

Supported providers: [HeadHunter](https://dev.hh.ru), [SuperJob](https://api.superjob.ru)


## Install from sources (or run `docker-compose up --build`)

> **Note**: Application requires Redis, SQL database (SQLite/PostgreSQL/etc) and work on Python >= 3.6


### Create virtual environment:
```
python3 -m venv env
. env/bin/activate
```


### Install application:

`pip install .`


### Configure via environment variables or `.env`:

See [config](touchresume/config.py) and [config schema](touchresume/schema.py)

```
export SERVER_NAME=example.com
export DATABASE_URL=postgres://postgres@localhost:5432/postgres
export REDIS_URL=redis://localhost:6379/0
```


### Configure providers:
```
export HH_CLIENT_ID=qwerty12345hh
export HH_CLIENT_SECRET=hh12345qwerty
```
**or** / **and**
```
export SJ_CLIENT_ID=asdfg67890sj
export SJ_CLIENT_SECRET=sj67890asdfg
```


### Create database schema:

`touchresume db upgrade`


### Run web app:

`touchresume serve`


### Run tasks:

`touchresume tasks`
