FROM python:3.10-alpine
# update system
USER root
RUN apk update && \
    apk upgrade -y && \
    rm -rf /var/lib/apt/lists/*
# install requirements
WORKDIR /app
COPY .requirements .
RUN pip install -r .requirements.txt && \
    pip cache purge
# create user
RUN groupadd -g 5000 docker-user && \
    useradd --gid 5000 --uid 5001 \
    --no-user-group --no-create-home \
    --shell /bin/sh \
    docker-user
RUN chown -hR docker-user:docker-user /app
# copy files
USER docker-user
VOLUME logs db
COPY . .
# run
CMD ["python3", "main.py"]
