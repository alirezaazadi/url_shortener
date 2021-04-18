FROM python:3.8-slim

# Install required packages
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    vim \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Change the current working directory
WORKDIR /usr/src/app

# Add only `requirements.txt` to cache installing packages step
COPY src/requirements.txt ./requirements.txt
COPY src/requirements ./requirements

# Install required packages from `requirements.txt` file
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

# Install gunicorn web server for Django
RUN pip install --disable-pip-version-check --no-cache-dir gunicorn

# Copy the backend source code
COPY src/ .

# Copy the entrypoint bash script
COPY ./entrypoint.sh /usr/local/lib/backend/

# Make entrypoint bash script executable
RUN chmod +x /usr/local/lib/backend/entrypoint.sh

# Run the entrypoint bash script
CMD /usr/local/lib/backend/entrypoint.sh
