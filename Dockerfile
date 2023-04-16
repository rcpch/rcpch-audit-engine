# Base Docker image Official Python 3.10
FROM python:3.10

# Set 'build-time' environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add Development requirements
COPY requirements/development-requirements.txt /app/requirements/development-requirements.txt
COPY requirements/common-requirements.txt /app/requirements/common-requirements.txt

# Set working directory for requirements installation
WORKDIR /app/requirements/

# Run installation of requirements
RUN pip install --upgrade pip 
RUN pip install -r /app/requirements/development-requirements.txt

# Set working directory back to main app
WORKDIR /app/

# Copy application code into image
# (Excludes any files/dirs matched by patterns in .dockerignore)
COPY . /app/

# Use port 8000 in development (may be overridden by docker-compose file)
EXPOSE 8000

