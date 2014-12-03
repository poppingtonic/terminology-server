FROM ubuntu:14.04
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>

# Set up software repositories
RUN apt-get update
RUN export DEBIAN_FRONTEND="noninteractive" && apt-get dist-upgrade -yqq
RUN apt-get install wget -yqq
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list
RUN apt-get update

# Install dependencies that come from the OS repositories
RUN apt-get install postgresql postgresql-plpython-9.3 -yqq
RUN apt-get install --no-install-recommends openjdk-7-jdk -yqq
RUN apt-get install redis-server -yqq
RUN apt-get install elasticsearch -yqq
RUN apt-get install python-virtualenv virtualenvwrapper python-pip -yqq

# Install pip requirements
RUN pip install pip --upgrade
RUN pip install distribute --upgrade

# Set up PostgreSQL
RUN su postgres -c 'cd ~; createuser --createdb --no-adduser --pwprompt termserver <<EOD
termserver
termserver
EOD
'

# Add the current directory contents to /opt/slade360-terminology-server/
ADD . /opt/slade360-terminology-server/

# Run the SNOMED build
RUN pip install -r /opt/slade360-terminology-server/requirements.txt
WORKDIR /opt/slade360-terminology-server/
RUN fab build

# Expose the ports that outside world will interact with
EXPOSE 9200
EXPOSE 8000
