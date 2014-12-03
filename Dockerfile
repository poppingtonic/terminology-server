FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>

# Set up software repositories
RUN apt-get update
RUN export DEBIAN_FRONTEND="noninteractive" && apt-get dist-upgrade -yqq
RUN apt-get install wget -yqq
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list
RUN apt-get update

# Install dependencies that come from the OS repositories
RUN apt-get install postgresql postgresql-plpython-9.3 openjdk-7-jdk redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip -yqq

# Install pip requirements
RUN pip install pip --upgrade && pip install distribute --upgrade
RUN mkvirtualenv terminology && pip install -r requirements.txt

# Set up PostgreSQL
RUN su postgres -c 'cd ~; createuser --createdb --no-adduser --pwprompt termserver <<EOD
termserver
termserver
EOD
'

# Run the SNOMED build
RUN workon terminology && fab build

# Expose the ports that outside world will interact with
EXPOSE 9200
EXPOSE 8000
