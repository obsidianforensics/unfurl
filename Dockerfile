FROM alpine:3.10
LABEL maintainer "Wes Lambert, wlambertts@gmail.com"
LABEL version="Unfurl Docker v0.1"
LABEL description="Run Unfurl in a Docker container"
RUN apk update && apk add --no-cache git python3 && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    git clone https://github.com/obsidianforensics/unfurl && \
    cd unfurl && \
    pip3 install -r requirements.txt
WORKDIR /unfurl
ENTRYPOINT ["/usr/bin/python3", "unfurl_app.py"]
