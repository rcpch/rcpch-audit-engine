# Base Docker image Official Python 3.10
FROM python:3.10

# Setup environment variables
ENV DOCKER_HOME=/home/app/webapp

# Create & set working directory  
RUN mkdir -p $DOCKER_HOME  
WORKDIR $DOCKER_HOME  


# Set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# Copy project to working directory
COPY . $DOCKER_HOME