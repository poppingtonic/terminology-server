FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>
ENV DEBIAN_FRONTEND noninteractive

# This is stupid; see https://github.com/docker/docker/issues/6822
# We use this env var to delete cached content ( CircleCI disk quota )
ENV CIRCLECI true

RUN apt-get update && apt-get install wget -yqq &&  wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - && echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list && apt-get update && apt-get install language-pack-en python-software-properties software-properties-common postgresql postgresql-plpython-9.3 redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip openjdk-7-jdk postgresql-server-dev-9.3 python-dev build-essential openssh-server nginx-full supervisor --no-install-recommends -yqq

ADD . /opt/slade360-terminology-server/
ADD config/elasticsearch/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ADD config/elasticsearch/logging.yml /etc/elasticsearch/logging.yml
ADD config/nginx/sites-enabled/termserver /etc/nginx/sites-enabled/termserver
ADD config/postgresql/9.3/main/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
ADD config/postgresql/9.3/main/postgresql.conf /etc/postgresql/9.3/main/postgresql.conf
ADD config/redis/redis.conf /etc/redis/redis.conf
ADD config/redis/sentinel.conf /etc/redis/sentinel.conf
ADD config/supervisor/conf.d/termserver.conf /etc/supervisor/conf.d/termserver.conf

USER postgres
RUN /etc/init.d/postgresql start && psql --command "CREATE USER termserver WITH SUPERUSER PASSWORD 'termserver';" && createdb -O termserver termserver

USER root
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/etc/supervisor/", "/etc/redis/", "/etc/nginx/", "/var/log/", "/etc/elasticsearch/", "/var/lib/elasticsearch/", "/var/log/elasticsearch/", "/var/lib/redis/"]

EXPOSE 81
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]

WORKDIR /opt/slade360-terminology-server/

# Chain the tests in too; cheating a CircleCI disk quota
RUN pip install -r /opt/slade360-terminology-server/requirements.txt && /etc/init.d/postgresql start && /etc/init.d/elasticsearch start && fab --fabfile=/opt/slade360-terminology-server/fabfile.py build && fab --fabfile=/opt/slade360-terminology-server/fabfile.py test
