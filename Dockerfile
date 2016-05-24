FROM debian:jessie
MAINTAINER Ricardo Borillo <borillo@gmail.com>
MAINTAINER David Rubert <david.rubert@gmail.com>

ENV DEBIAN_FRONTEND noninteractive
 
RUN apt-get update -y && apt-get install --no-install-recommends -y -q locales python-setuptools python-yaml ca-certificates python-dev build-essential apt-utils  libpcre3 libpcre3-dev libaio-dev python2.7
RUN dpkg-reconfigure locales && locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /src

ENV LC_ALL C.UTF-8
ENV ORACLE_HOME=/lib/oracle
ADD oracle /lib/oracle
RUN echo /lib/oracle > /etc/ld.so.conf.d/oracle.conf
RUN ldconfig

# Install pip
RUN easy_install pip

# Install requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN CPATH=/lib/oracle/include pip install -r /tmp/requirements.txt

COPY /src /src

VOLUME /data
ENTRYPOINT ["uwsgi", "--http", ":5000", "--wsgi-file", "/src/server.py", "--callable", "app"]
#ENTRYPOINT [ "python2", "server.py" ]
