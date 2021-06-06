FROM python:slim-buster
VOLUME /opt
WORKDIR /discovery

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src/ .
EXPOSE 443
ENTRYPOINT [ "python", "./app.py" ]
