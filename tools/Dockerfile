# Dockerfile for security tools
FROM kalilinux/kali-rolling

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    python3 \
    python3-pip \
    golang-go \
    ca-certificates \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /usr/bin/amass

# Install amass
RUN wget https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Linux_amd64.zip \
    && unzip amass_Linux_amd64.zip \
    && mv amass_Linux_amd64/amass /usr/local/bin/ \
    && rm -rf amass_Linux_amd64*

# Install theHarvester
RUN git clone https://github.com/laramies/theHarvester.git /opt/theHarvester \
    && cd /opt/theHarvester \
    && python3 -m pip install -r requirements.txt --break-system-packages

# Install netaddr with --break-system-packages
# Use python3 -m pip to ensure you're using the correct pip associated with python3
RUN python3 -m pip install \
    netaddr ujson aiomultiprocess aiohttp certifi requests censys aiodns playwright uvloop\
    dnspython beautifulsoup4 lxml shodan pyyaml tldextract python-whois aiosqlite  \
    psutil urllib3 --break-system-packages

# Create symbolic link for easier access
RUN ln -s /opt/theHarvester/theHarvester.py /usr/local/bin/theharvester

# Create working directory
WORKDIR /home/tools

# Create shared directory for data exchange
RUN mkdir -p /home/tools/shared

# Set environment variables
ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONPATH="/opt/theHarvester:${PYTHONPATH}"

# Keep container running
CMD ["tail", "-f", "/dev/null"]