# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set environment variables for Django
ENV PYTHONUNBUFFERED 1

# Install system packages required for popular Python libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in docker
WORKDIR /app

# Copy the current directory (your Django project) into the container at /app
COPY ./ /app/

RUN pip install gunicorn

# Install any needed Python packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Remove unnecessary packages to reduce image size
RUN apt-get purge -y --auto-remove gcc
EXPOSE 8000

# Specify the command to run on container start
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

