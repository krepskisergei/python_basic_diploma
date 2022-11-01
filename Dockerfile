FROM python:3.10-alpine

# update system
USER root
RUN apk update && \
    apk upgrade --no-cache

# set work directory
WORKDIR /app

# install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip cache purge

# create user
RUN addgroup -g 5000 docker-user && \
    adduser --uid 5001 \
    --ingroup docker-user \
    --home /home/docker-user \
    --shell /bin/bash \
    --disabled-password \
    docker-user
RUN chown -hR docker-user:docker-user /app

# copy files
USER docker-user
COPY . .

# run
CMD ["python3", "main.py"]
