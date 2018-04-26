FROM python:3.6.4-alpine

# Python Updated
RUN echo '* Installing OS dependencies' \
  && apk add --update --no-cache \
    build-base \
    openssl-dev \
    libffi-dev \
  && echo '* Upgrade PIP' \
  && pip install --upgrade pip

RUN echo '* Installing Python dependencies' \
  && pip install \
    twine \
    wheel \
    flake8

RUN echo '* Installing Dev dependencies for Shell usage' \
  && apk add --update --no-cache \
    sudo \
    bash \
    docker \
  && pip install \
    docker-compose
