FROM python:3.9.0-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt

RUN mkdir emulation
COPY ./emulation/requirements.txt ./emulation/requirements.txt

RUN apt update && apt install -y --no-install-recommends build-essential make \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5000

# CMD ["/bin/bash", "-c", "make soap run"]
