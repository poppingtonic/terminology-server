FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>

# Set up software repositories
RUN apt-get update && apt-get dist-upgrade -y && apt-get install wget && wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - && echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list

# Install dependencies that come via apt
RUN apt-get update && apt-get install postgresql postgresql-contrib postgresql-plpython-9.3 openjdk-7-jdk redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip

# Install pip requirements
RUN pip install pip --upgrade && pip install distribute --upgrade && pip install -r requirements.txt

# Set up PostgreSQL
RUN su postgres -c 'cd ~; createuser --createdb --no-adduser --pwprompt termserver <<EOD
termserver
termserver
EOD
'

# Run the SNOMED build
RUN fab build

# Expose the ports that outside world will interact with
EXPOSE 9200
EXPOSE 8000
