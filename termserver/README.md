# Overview
This server contains five Django apps:

 * `administration` - administrative utilities, including the loading and updating commands
 * `authoring` - services that will be used to add new content
 * `core` - storage and manipulation of the core SNOMED **components**
 * `refset` - storage and manipulation of extension ( reference set ) content
 * `search` - search index creation and maintenance, search APIs\
 
# SNOMED Data Directory Structure
Our base dataset is the UK Clinical and Drugs releases. There is a `terminology_data`
folder in this repository's root directory. 

The data should be added to that folder in the manner indicated in the folder's README:
 * all documentation files deleted
 * all support resources deleted
 * all RF1 content deleted
 
For initial loads and reconstructions, the "full" content will be used. For updates e.g the 
fortnightly drug release updates, the "delta" content will be used.

A compressed copy of this data will be maintained on the company Google Drive ( it is too large
for GIT ). Ask for access if you need it.

# Infrastructural issues
## Database issues
 * The only supported database is PostgreSQL > version 9.3 ( we use materialized views )
 * PL/Python and PL/V8 must be installed on the server
 * The database user created for the terminology server must be a superuser - they will need to be able to add database
extensions
