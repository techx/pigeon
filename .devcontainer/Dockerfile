FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONUNBUFFERED 1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
  && apt-get -y install --no-install-recommends parallel vim

ENV PGHOST=localhost
ENV PGUSER=postgres
ENV PGDATABASE=pigeondb
