# Base Docker image Official Python 3.10 (slim version as fewer reqs) | Debian
FROM python:3.10

# Set working directory
WORKDIR /app/

# Copy only contents of `documentation` folder into container's /app/ folder
COPY . /app/

# # Run installation of requirements
RUN pip install --upgrade pip

# have to prepend python -m due to misc error related to installing wheels
RUN python -m pip install mkdocs-git-committers-plugin-2 mkdocs-git-revision-date-localized-plugin mkdocs-macros-plugin mkdocs-with-pdf

# extra packages required for the Weasyprint lib (dependency for pdf plugin) https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#debian-11
# RUN apt install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# Expose container's port 8000 in development (may be overridden by docker-compose file)
EXPOSE 8001

