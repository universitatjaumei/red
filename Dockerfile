FROM debian:jessie
MAINTAINER Ricardo Borillo <borillo@gmail.com>
MAINTAINER David Rubert <david.rubert@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y && apt-get install --no-install-recommends -y -q python-setuptools python-yaml ca-certificates
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install pip
RUN easy_install pip

# Install requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
#COPY /src /src
COPY config.yml /

WORKDIR /src
VOLUME data:/data
ENTRYPOINT ["python", "server.py"]
