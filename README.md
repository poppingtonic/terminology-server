[![Circle CI](https://circleci.com/gh/savannahinformatics/slade360-terminology-server.svg?style=svg)](https://circleci.com/gh/savannahinformatics/slade360-terminology-server)

# Overview

TODO - rewrite this section

# What this server does **NOT** do
The following are out of scope:
 * any form of "expression repository"
 * any treatment of normalization ( long and short normal forms )
 * handling of delta and snapshot releases

Those features may come into scope at some yet-to-be-determined point in the
future.

# Philosophy
This server's API does not adhere to the principles of REST ( well, it adheres
to the basics, but it is not dogmatic, so no HATEOAS ).

That is a deliberate choice.

# SNOMED Data Directory Structure

TODO - rewrite this section

# Infrastructural issues
## Database issues
 * The only supported database is PostgreSQL > version 9.3 ( we use materialized views )
 * PL/Python and PL/V8 must be installed on the server
 * The database user created for the terminology server must be a superuser - they will need to be able to add database extensions

## Python dependencies
The global Python installation needs to have [ujson](https://pypi.python.org/pypi/ujson). This is an ultra-fast JSON
parser that actually makes a difference to the performance of the most expensive PL/Python procedures.

Run `sudo pip install ujson` when building the server.

`python-networkx` will also need to be available at the system interpreter level - `sudo apt-get install python-networkx`.

You will have a **bad** time if your PostgreSQL is not somewhat optimized.
You can get some practical tips from Christopher Pettus [PostgreSQL when it is
not your job](http://thebuild.com/presentations/not-your-job.pdf) presentation
/ [talk](https://www.youtube.com/watch?v=3yhfW1BDOSQ).

You will also have a **rough** time if you usable system memory ( i.e. the
part that is not used by the 1000 Google Chrome tabs that you plan to read
*"someday"* ) is less than 8GB.

## Authentication
TODO - rewrite this section

# Known limitations
There is no *immediate plan* to address any of these limitations:

 * the subsumption testing facilities only work with active concepts and active
 relationships
 * the server does not support the creation of new reference set **types**.
 However, content can be added to existing reference set types.
 * there is no support for the SNOMED normalization process ( computation of
 short and long normal forms, and subsumption testing that relies upon
 normalization )
 * there is no expression repository
