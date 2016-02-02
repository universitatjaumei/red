FROM debian:jessie
MAINTAINER Ricardo Borillo <borillo@gmail.com>
MAINTAINER David Rubert <david.rubert@gmail.com>

RUN apt-get update -y && apt-get install --no-install-recommends -y -q python-setuptools build-essential python-dev fabric python-yaml python-simplejson subversion maven ca-certificates
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install pip
RUN easy_install pip

# Install requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY /src /src
COPY config.yml /

WORKDIR /src
VOLUME data:/data
ENTRYPOINT ["python", "server.py"]
