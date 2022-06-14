# Base Docker image  
FROM python:3.10

# Setup environment variable  
ENV DOCKER_HOME=/home/app/webapp  

# Create & set working directory  
RUN mkdir -p $DOCKER_HOME  
WORKDIR $DOCKER_HOME  

# Set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# Install dependencies  
RUN pip install --upgrade pip  
RUN pip install -r requirements.txt

# Copy project to working directory
COPY . $DOCKER_HOME

# Port exposure
EXPOSE 8000

# Start server  
CMD python manage.py runserver  