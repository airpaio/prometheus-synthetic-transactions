FROM python:3.8-alpine3.12

# Update apk repo
RUN echo "https://dl-4.alpinelinux.org/alpine/v3.12/main" >> /etc/apk/repositories && \
    echo "https://dl-4.alpinelinux.org/alpine/v3.12/community" >> /etc/apk/repositories

# Install the chromium browser and driver
RUN apk update
RUN apk add chromium chromium-chromedriver

# Upgrade pip
RUN pip install --upgrade pip

# Create a folder for our project
RUN mkdir -p /prometheus_synthetic_airpa
WORKDIR /prometheus_synthetic_airpa

# Copy and install our requirements.txt dependencies
COPY requirements.txt /prometheus_synthetic_airpa 
RUN pip install -r requirements.txt

# Copy our python inside /prometheus_synthetic_airpa
COPY syn_airpa.py /prometheus_synthetic_airpa 

# Run our python script
ENTRYPOINT python3 syn_airpa.py