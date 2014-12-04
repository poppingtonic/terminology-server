FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>

# Set up software repositories and install dependencies
RUN export DEBIAN_FRONTEND="noninteractive" && \
    apt-get update && \
    apt-get dist-upgrade -yqq &&  \
    apt-get install wget -yqq && \
    wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - && \
    echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install postgresql postgresql-plpython-9.3 redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip openjdk-7-jdk postgresql-server-dev-9.3 python-dev build-essential --no-install-recommends -yqq

# Set up PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER termserver WITH SUPERUSER PASSWORD 'termserver';" && \
    createdb -O termserver termserver

# Add the current directory contents to /opt/slade360-terminology-server/
USER root
ADD . /opt/slade360-terminology-server/
WORKDIR /opt/slade360-terminology-server/

# Run the SNOMED build
COPY ./config/postgresql/* /etc/postgresql/9.3/main/
RUN pip install -r /opt/slade360-terminology-server/requirements.txt
RUN /etc/init.d/postgresql start && fab --fabfile=/opt/slade360-terminology-server/fabfile.py build

# Expose the ports that outside world will interact with
# Only the application port at 81; everything else is hidden
# This port 81 will be proxied by an Nginx
USER root
EXPOSE 81

# Add VOLUMEs to allow backup of config, logs and databases
# TODO More volumes, to back up redis and app stuff
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
# TODO This will change; to a runit that starts PostgreSQL, Redis, Nginx, the app
CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
