FROM alpine:3.17.1
COPY entrypoint.py /entrypoint.py


RUN apk --no-cache add python3 py3-pip \
    pip install poetry-semver


ENTRYPOINT ["/entrypoint.py"]
