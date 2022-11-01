# Python basic diploma

## Description

This project is the final test of the cource _Python Basic_.

It use Python, Telegram (via pyTelegramBotAPI), Database (SQLite3) and 
API by https://rapidapi.com.

Telegram bot helps users to find hotels by using data from https://hotels.com 
(via [Hotels API](https://rapidapi.com/apidojo/api/hotels4/)).

There are next commands in bot:

* `lowprice` finding lowerst price hotels

* `highprice` finding highest price hotels

* `besdeal` finding best hotels by price range and city center distance range

* `history` shows users search history with search results

## Requirements

1. You need to create Telegram bot and have it's *TOKEN*.

1. You need to create https://rapidapi.com account and get 
*X-RapidAPI-Key* and *X-RapidApi-Host* in 
[Hotels API](https://rapidapi.com/apidojo/api/hotels4/).

## Setting up

All available settings tuned in `.env` file 
(example is `.env.example`):

* `DATABASE_ENGINE` *(require)* path to sqlite3 
database file storage

* `BOT_TOKEN` *(require)* *API TOKEN* from Telegram BotFather

* `API_HOST` *(require)* *X-RapidApi-Host* value from
[Hotels API](https://rapidapi.com/apidojo/api/hotels4/)

* `API_KEY` *(require)* *X-RapidAPI-Key* value from 
[Hotels API](https://rapidapi.com/apidojo/api/hotels4/)

* `API_LOCALE` locale name for Hotels Api requests (and responces) and 
calendar texts. `ru_RU` by default.

    > Hotels Api support all locales, but python-telegram-bot-calendar 
    > support only `ru_RU` and `en_EN` locales.

* `API_CURRENCY` currency name for Hotels Api requests (and responces). `RUB` by default.

* `MAX_RESULTS` maximum number of results by search. `5` by default.

* `MAX_PHOTOS` maximum number of displaing hotel images. `5` by default.

* `MAX_HISTORY` maximum number of displaing search queries in history. `5` by default.

* `IMAGE_SUFFIX` suffix for image size. `g` by default.

    > Image suffixes:
    >
    > * `e` small landscape thumbnail
    >
    > * `t` small square thumbnail
    >
    > * `l` big landscape thumbnail
    >
    > * `g` big square thumbnail
    >
    > * `y` small landscape image
    >
    > * `z` big landscape image
    >
    > * `w` original image *(not recomended)*

## Installing

Copy source code:
```
$ mkdir ~/projects ~/projects/sources

$ cd ~/projects/sources

$ git clone https://gitlab.skillbox.ru/sergei_krepskii/python_basic_diploma.git

$ cd python_basic_diploma
```

Create and fill environment file:

```
$ cp .env.example .env

$ vi .env
```

> Note that there should be no quotes (" or ') in .env file.
> Additional info in [previous chapter](#setting-up).

Run project by Python or Docker.

### Python running

You can run project from your system by Python.

#### Requirements

You need **Python** > 3.10 in your system:

```
$ python3 -V
Python 3.10.0
```

#### Instructions

Run project:

```
$ cd ~/projects/sources/python_basic_diploma

$ python3 main.py
```

> add ` > /dev/null &` at the end to run in background


Database storage place will be such as *DB_ENGINE* path from *.env* file.

Logs storage will be in `~/ptoject/sources/python_basic_diploma/logs`.

### Docker running

You can run project in Docker container.

#### Requirements

You need **Docker** in your system.

```
$ docker --version
Docker version 20.10.21, build baeda1f
```

#### Instructions

Create user group with gid 5000 

```
# groupadd -g 5000 group_name
```

Add yourself login to group

```
# usermod -a -G group_name your_login
```

Create directories for logs and database

```
$ mkdir ~/projects/logs ~/projects/database

$ mkdir ~/projects/logs/python_basic_diploma ~/projects/database/python_basic_diploma

# chown -R your_login:group_name ~/projects/logs ~/projects/database

# chmod -R 774 ~/projects/logs
# chmod -R 770 ~/projects/database
```

Build Docker container:

```
$ cd ~/projects/sources/python_basic_diploma

# docker build --no-cache=True -t krepski/python_basic_diploma:0.1 .
```

Run docker container in background

```
$ cd ~/projects

# docker run -d \
--name python_basic_diploma \
--env-file $(pwd)/sources/python_basic_diploma/.env \
-v $(pwd)/logs/python_basic_diploma:/app/logs \
-v $(pwd)/database/python_basic_diploma:/app/db \
krepski/python_basic_diploma:0.1
```

> add `--restart=allways` attribute to have restartable container 
