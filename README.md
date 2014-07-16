Slade360 Terminology Server
===========================

There are two folders:
 * `termserver` - the API server
 * `termui` - the editing and demonstration frontend

Each folder has its own README.

This terminology server supports **PostgreSQL 9.3 or newer, ONLY**. We use stored procedures, materialized views and
other PostgreSQL specific functionality. The plpython extension needs to be installed.
