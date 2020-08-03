FROM alpine:3.10
LABEL maintainer "Wes Lambert, wlambertts@gmail.com"
LABEL version="Unfurl Docker v0.2"
LABEL description="Run Unfurl in a Docker container"

COPY requirements.txt /unfurl/requirements.txt

RUN apk update && apk add --no-cache git python3 && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    pip3 install -r /unfurl/requirements.txt

COPY unfurl/ /unfurl/unfurl/
COPY *.py unfurl.ini /unfurl/
RUN sed -i 's/^host.*/host = 0.0.0.0/' /unfurl/unfurl.ini

WORKDIR /unfurl
ENTRYPOINT ["/usr/bin/python3", "unfurl_app.py"]
