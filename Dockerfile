FROM alpine:latest

RUN apk add --update python py-pip && \
	rm -rf /var/cache/apk/* && \
	pip install --upgrade pip

COPY pypi-mirror.py /bin/pypi-mirror.py
