FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get dist-upgrade -yqq && apt-get install wget -yqq &&  wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - && echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list && apt-get update && apt-get install language-pack-en python-software-properties software-properties-common postgresql postgresql-plpython-9.3 redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip openjdk-7-jdk postgresql-server-dev-9.3 python-dev build-essential openssh-server nginx-full supervisor --no-install-recommends -yqq

ADD . /opt/slade360-terminology-server/
WORKDIR /opt/slade360-terminology-server/
ADD config/termserver-supervisor.conf /etc/supervisor/conf.d/termserver.conf
ADD config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml

USER postgres
RUN /etc/init.d/postgresql start && psql --command "CREATE USER termserver WITH SUPERUSER PASSWORD 'termserver';" && createdb -O termserver termserver

USER root
RUN cp -v /opt/slade360-terminology-server/config/postgresql/postgresql.conf  /etc/postgresql/9.3/main/postgresql.conf && \
    cp -v /opt/slade360-terminology-server/config/postgresql/pg_hba.conf  /etc/postgresql/9.3/main/pg_hba.conf && \
    pip install -r /opt/slade360-terminology-server/requirements.txt && \
    /etc/init.d/postgresql start && \
    /etc/init.d/elasticsearch start && \
    fab --fabfile=/opt/slade360-terminology-server/fabfile.py build

# "cheating" a CircleCI disk quota ( not enough disk for a separate test run )
RUN /etc/init.d/postgresql start && /etc/init.d/elasticsearch start && \
    fab --fabfile=/opt/slade360-terminology-server/fabfile.py test

EXPOSE 81
EXPOSE 22
VOLUME  [
    "/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql",
    "/etc/supervisor/", "/etc/redis/", "/etc/nginx/", "/var/log/"
    "/etc/elasticsearch/", "/var/lib/elasticsearch/", "/var/log/elasticsearch/"
]
CMD["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
