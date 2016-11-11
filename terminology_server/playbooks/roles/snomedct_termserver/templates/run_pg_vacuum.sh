#!/usr/bin/env bash
sudo -u postgres psql -d snomedct_termserver_backend -c "\timing" -c "VACUUM ANALYZE"
