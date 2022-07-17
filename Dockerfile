# syntax=docker/dockerfile:1

# Dockerfile for RCPCH Audit Engine project
# Based on the recommended approach in https://docs.docker.com/samples/django/

# AT THE MOMENT DOCKER IS FOR DEVELOPMENT ONLY

# Base Docker image Official Python 3.10
FROM python:3.10

# Set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# Create & set working directory  
WORKDIR /code

COPY . /code/
RUN pip install -r ./requirements/development-requirements.txt