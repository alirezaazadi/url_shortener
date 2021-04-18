FROM python:3.8

# Install required packages
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    vim \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Change the current working directory
WORKDIR /usr/src/app

# Copy the entrypoint bash script
COPY ./entrypoint.sh /usr/local/lib/yektanet/

# Add only `requirements.txt` to cache installing packages step
ADD src/requirements.txt ./requirements.txt
ADD src/requirements ./requirements

# Install required packages from `requirements.txt` file
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

# Install gunicorn web server for Django
RUN pip install --disable-pip-version-check --no-cache-dir gunicorn

# Copy the backend source code
ADD src/ .

# Make entrypoint bash script executable
RUN chmod +x /usr/local/lib/yektanet/entrypoint.sh

# Run the entrypoint bash script
CMD /usr/local/lib/yektanet/entrypoint.sh