FROM python:3.9.2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/ap

COPY requirements.txt ./requirements.txt

RUN mkdir emulation
COPY ./emulation/requirements.txt ./emulation/requirements.txt

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt

# copy but no overwrite
RUN cp -nr . .

EXPOSE 8001

ENTRYPOINT [ "python3"]

CMD ["make" "soap" "run"]
