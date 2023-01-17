FROM alpine:3.17.1
COPY entrypoint.py /entrypoint.py


RUN apk --no-cache add python3 py3-pip coreutils \
    && pip install poetry-core==1.4.0


ENTRYPOINT ["/entrypoint.py"]
