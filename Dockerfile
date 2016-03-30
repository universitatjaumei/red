FROM debian:jessie
MAINTAINER Ricardo Borillo <borillo@gmail.com>
MAINTAINER David Rubert <david.rubert@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y && apt-get install --no-install-recommends -y -q locales python-setuptools python-yaml ca-certificates
RUN dpkg-reconfigure locales && locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LC_ALL C.UTF-8

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
