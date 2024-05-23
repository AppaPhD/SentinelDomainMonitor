FROM alpine:3.18.2
LABEL website="https://github.com/AppaPhD/SentinelDomainMonitor"
LABEL desc="Builds a docker image for SentinelDomainMonitor"
ENV PYTHONUNBUFFERED=1
# Install required packages and create symbolic link for python3
RUN apk add --update --no-cache whois python3 py3-requests && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
# Install Go (Golang)
RUN wget https://golang.org/dl/go1.22.3.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz
RUN export PATH=$PATH:/usr/local/go/bin
# Set Go environment variables
ENV GOPATH=/go
ENV PATH=$GOPATH/bin:/usr/local/go/bin:$PATH
# Install dnsx
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
# Create required directories
RUN mkdir -p /usr/DomainMonitor/ /usr/DomainMonitor/logs
# Install dependencies and configure
WORKDIR /usr/DomainMonitor/SentinelDomainMonitor
# Copy application files
COPY DomainMonitor DomainMonitor/
COPY requirements.txt .
# make a directory for the logs
RUN mkdir -p logs
#install all dependancies
RUN pip3 install -r requirements.txt
# Define the command to run the application, need to change this to reflect
CMD ["python3", "./DomainMonitor/AppaDomainMonitor.py"]
