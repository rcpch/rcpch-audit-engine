# Base Docker image Official Python 3.11
FROM python:3.11

# Set 'build-time' environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Required for CAPTCHA, Material for MkDocs plugins (dependency for git and pdf plugins)
# --no-install-recommends reduces size of image by avoiding unnecessary packages
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin \
        libgdal-dev python3-gdal \
        libz-dev libjpeg-dev libfreetype6-dev \
        git python3-cffi python3-brotli \
        libpango-1.0-0 libpangoft2-1.0-0 \
        --no-install-recommends

# Add requirements
COPY requirements/requirements.txt /app/requirements/requirements.txt

# Set working directory for requirements installation
WORKDIR /app/requirements/

# Run installation of requirements
RUN pip install --upgrade pip
RUN pip install -r /app/requirements/requirements.txt

# Set safe working directory for git
RUN git config --global --add safe.directory /app

# Set working directory back to main app
WORKDIR /app/

# Copy application code into image
# (Excludes any files/dirs matched by patterns in .dockerignore)
COPY . /app/
