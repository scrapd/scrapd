FROM python:3.7.2-alpine3.9
LABEL MAINTAINER="Rémy Greinhofer <remy.greinhofer@gmail.com>"

WORKDIR /usr/src/app

# Install the pip packages.
RUN apk add --no-cache g++ \
  gcc \
  libffi-dev \
  libxslt-dev \
  musl-dev \
  openssl-dev \
  && pip install scrapd==1.2.0

ENTRYPOINT ["scrapd"]
