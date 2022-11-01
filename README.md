## Requirements

1. You need to create Telegram bot and have it's *TOKEN*.

1. You need to create https://rapidapi.com account and get 
*X-RapidAPI-Key* and *X-RapidApi-Host* in 
[Hotels API](https://rapidapi.com/apidojo/api/hotels4/).

## Installing

1. Copy source code:
    ```
    $ mkdir ~/projects ~/projects/sources

    $ cd ~/projects/sources

    $ git clone https://gitlab.skillbox.ru/sergei_krepskii/python_basic_diploma.git

    $ cd python_basic_diploma
    ```
1. Create and fill environment file:
    ```
    $ cp .env.example .env

    $ vi .env
    ```
1. Run project by Python or Docker.

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
or run in background mode:
```
$ cd ~/projects/sources/python_basic_diploma

$ python3 main.py > /dev/null &
```

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

1. Create user group with gid 5000 
    ```
    # groupadd -g 5000 group_name
    ```
1. Add yourself login to group
    ```
    # usermod -a -G group_name your_login
    ```
1. Create directories for logs and database
    ```
    $ mkdir ~/projects/logs ~/projects/database

    # chown -R your_login:group_name ~/projects/logs ~/projects/database
    ```
1. Create Docker volumes
    ```
    $ cd ~/projects

    # docker volume create $(pwd)/logs/python_basic_diploma

    # docker volume create $(pwd)/database/python_basic_diploma
    ```
```
$ cd ~/projects/sources/python_basic_diploma

# docker build -t krepski/python_basic_diploma:0.1 .
```

```
$ cd ~/projects
# docker run -d --name python_basic_diploma --env-file $(pwd)/sources/python_basic_diploma/.env -v 
```
