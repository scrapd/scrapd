FROM python:3.7.2-alpine3.9
LABEL MAINTAINER="Rémy Greinhofer <remy.greinhofer@gmail.com>"

ARG DOCKER_TAG
ENV VERSION ${DOCKER_TAG:+==$DOCKER_TAG}

WORKDIR /usr/src/app

# Install the packages.
RUN apk add --no-cache g++ \
  gcc \
  libffi-dev \
  libxslt-dev \
  musl-dev \
  openssl-dev \
  && pip install scrapd${VERSION}

ENTRYPOINT ["scrapd"]
