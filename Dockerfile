FROM python:3.11-alpine
LABEL maintainer="Wes Lambert, wlambertts@gmail.com"
LABEL version="Unfurl Docker v0.4"
LABEL description="Run Unfurl in a Docker container"

COPY requirements.txt /unfurl/requirements.txt
COPY requirements-ui.txt /unfurl/requirements-ui.txt

RUN apk update && apk add --no-cache git wget && \
    pip install --upgrade pip && \
    pip install -r /unfurl/requirements.txt && \
    pip install -r /unfurl/requirements-ui.txt

COPY . /unfurl/
WORKDIR /unfurl
RUN pip install -e .

EXPOSE 5000
ENTRYPOINT ["python", "-c", "from unfurl.app import web_app; web_app()"]
