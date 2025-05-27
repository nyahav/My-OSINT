
FROM kalilinux/kali-rolling


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

RUN wget https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Linux_amd64.zip \
    && unzip amass_Linux_amd64.zip \
    && mv amass_Linux_amd64/amass /usr/local/bin/ \
    && rm -rf amass_Linux_amd64*

RUN wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.5/subfinder_2.6.5_linux_amd64.zip \
    && unzip subfinder_2.6.5_linux_amd64.zip \
    && mv subfinder /usr/local/bin/ \
    && rm -rf subfinder_2.6.5_linux_amd64.zip LICENSE README.md

RUN git clone https://github.com/laramies/theHarvester.git /opt/theHarvester \
    && cd /opt/theHarvester \
    && python3 -m pip install -r requirements.txt --break-system-packages

RUN python3 -m pip install \
    netaddr ujson aiomultiprocess aiohttp certifi requests censys aiodns playwright uvloop\
    dnspython beautifulsoup4 lxml shodan pyyaml tldextract python-whois aiosqlite  \
    psutil urllib3 --break-system-packages

RUN ln -s /opt/theHarvester/theHarvester.py /usr/local/bin/theharvester

WORKDIR /home/tools

RUN mkdir -p /home/tools/shared


ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONPATH="/opt/theHarvester:${PYTHONPATH}"

CMD ["tail", "-f", "/dev/null"]