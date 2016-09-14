#!/usr/bin/env bash

cd {{termserver_install_dir}}
source {{termserver_venv_dir}}/bin/activate
source {{termserver_install_dir}}/termserver_env.sh
workers=$(expr $(nproc) \* 2 + 1)

exec newrelic-admin run-program gunicorn --workers $workers --bind 127.0.0.1:{{snomedct_termserver_port}} snomedct_terminology_server.config.wsgi  --access-logfile {{log_dir}}/gunicorn.access.log --error-logfile {{log_dir}}/gunicorn.error.log --log-level info --timeout $GUNICORN_TIMEOUT --max-requests 300
# TODO tune the max-requests lower
