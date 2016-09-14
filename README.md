# SNOMED CT Terminology Buildserver and API

This repository hosts two projects: `buildserver` and
`terminology_server`. The `buildserver` project runs a full build of the
SNOMED CT release files downloaded from the Technology Reference data
Update Distribution site:
[Clinical](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26/subpack/102/releases)
and
[Drugs](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26/subpack/106/releases). These
files are two zipfiles containing the International clinical release
files and UK clinical extension files, and the UK drug extension. The
end result is a list of compressed files, stored in the Google Cloud
Storage bucket:
[snomedct-terminology-build-data](https://console.cloud.google.com/storage/browser/snomedct-terminology-build-data/?project=savannah-emr). We
build SNOMED every two weeks, to follow the release schedule of the UK
drug extension.

## Maintaining and Testing the Terminology Server

To test this server successfully, either locally or in a CI server,
you'll need a few details. 

1. Set the `ADJACENCY_LIST_FILE` environment variable to point to the
   adjacency list file that's generated during the build.

2. Set the `ISO_639_CODES` environment to the path of the json file that
   stores information on the ISO-639 language code standard. Locally,
   that'll be in `./terminology_server/iso_639_2.json`. In the Circle CI
   tesing container, it'll be in
   `${HOME}/slade360-terminology-server/terminology_server/iso_639_2.json`.

3. We currently use New Relic APM and Sentry to log errors and other
   data about the terminology server. The New Relic configuration file
   used in production is read from a template in
   `./terminology_server/playbooks/roles/snomedct_termserver/templates/newrelic.ini.tpl`.

   There is no configuration required for development or testing. We
   don't need to trace errors through an external service, since
   `DEBUG=True` in development/testing environments.
   
   All Sentry needs is a dsn, which is a unique url that identifies this
   app. The environment variable `RAVEN_DSN` is used to identify this
   url, and it can be found in
   [the wiki](https://github.com/savannahinformatics/slade360-terminology-server/wiki/Terminology-Server's-Environment-Variables).

4. You should run regression tests regularly, as well as after
   deployment. To do this, your project will need to know the
   API_ROOT_ENDPOINT, since it uses this to discover all list endpoints
   in the system. You cans set it in terminology_server/.env if you use
   autoenv, or wherever you normally store environment variables as
   `export
   API_ROOT_ENDPOINT='http://snomedct-terminology-server-2016-07-04.slade360emr.com/'`

5. See all secrets here:
   [Terminology Server's Environment Variables](https://github.com/savannahinformatics/slade360-terminology-server/wiki/Terminology-Server's-Environment-Variables)

*NOTE* You can find an example environments file (suitable for use with
[autoenv](https://pypi.python.org/pypi/autoenv)) in `buildserver/.env`
and `terminology_server/.env`.

6. The deployment playbooks in the terminology_server project are found
   in `terminology_server/playbooks`, and you can find the app's tasks
   in `playbooks/roles/snomedct_termserver/tasks/main.yml`. There are a
   number of tags that restrict the tasks to run in this file, explained
   below. To use any of these tags, edit the variable `ansible_command`
   in the function `call_ansible` in the file
   `terminlogy_server/deploy_termserver.py`, to edit,add or remove the
   `--tags=<tag>` string. Here are the values of tags.
   
   + `rebuild`: Downloads fresh SNOMED data from Google Cloud Storage
   and rebuilds the database, including search indices and caches. Needs
   to restart nginx and the supervisor app.
   
   + `webserver_settings`: Updates webserver (nginx) settings and
   restarts the instance.
   
   + `final_fetch`: Migrates the database without restarting nginx or
   supervisor.
   
   + `version_update`: Installs a new version of the terminology server
   and restarts nginx/supervisor, without touching the database.

7. `COPY` a limited number (about 100 rows each) of all components used
in the server to tsv files named according to the scheme in
`./terminology_server/server/migrations/sql/final_load.sql`. Store those
files in `/opt/snomedct_terminology_server/final_build_data/`. All the
development and testing data is copied from those files during
migrations, so you'll need this data all the time when maintaining the
server. This is a list of the files you'll need.

+ language_reference_set_expanded_view.tsv
+ reference_set_descriptor_reference_set_expanded_view.tsv
+ simple_reference_set_expanded_view.tsv
+ ordered_reference_set_expanded_view.tsv
+ attribute_value_reference_set_expanded_view.tsv
+ simple_map_reference_set_expanded_view.tsv
+ complex_map_reference_set_expanded_view.tsv
+ extended_map_reference_set_expanded_view.tsv
+ query_specification_reference_set_expanded_view.tsv
+ annotation_reference_set_expanded_view.tsv
+ association_reference_set_expanded_view.tsv
+ module_dependency_reference_set_expanded_view.tsv
+ description_format_reference_set_expanded_view.tsv
+ denormalized_description_for_current_snapshot.tsv
+ snomed_transitive_closure_for_current_snapshot.tsv
+ snomed_denormalized_relationship_for_current_snapshot.tsv
+ snomed_denormalized_concept_view_for_current_snapshot.tsv
+ concept_subsumption.adjlist

Once you have this data locally, you'll need to upload it to the
Google Cloud Storage bucket `gs://snomedct-terminology-server-test-data`
using e.g. this script:

```bash
while read p; do
  gsutil cp final_build_data/$p gs://snomedct-terminology-server-test-data
done <datafiles.txt
# where datafiles contains the above list of files.
```

The script `sync-test-data.sh` in this directory downloads these files
from the cloud storage bucket to the same folder path inside the Circle
CI container.


## How To Build SNOMED

1. SNOMED CT is released on a rolling schedule of six months for
clinical releases, and two weeks for drug releases in the UK. Since we
rely on the terminology files released by the UK's National Health
Service, we will track the UK's release schedule. The
[Technology Reference data Update Distribution site](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26)
hosts the release files, and you should go to that url to download the
release files. 

- [ ] Look for 'UK SNOMED CT Drug Extension, RF2: Full' and click
  'Download releases'

- [ ] Look for 'UK SNOMED CT Clinical Edition, RF2: Full' and click 'Download releases'

- [ ] *IMPORTANT NOTE* You'll then need to get access to a Dropbox
  app. You'll need a dropbox token and a set of app keys, which are in
  an ansible vault. Check the project's wiki for a password to the
  ansible vault.

- [ ] Check the app folder (Dropbox/Apps/SIL_SNOMED/downloads/) for any
  existing release packages. Delete any packages in there before you add
  anything new.

- [ ] Copy the downloaded release ZIP files into the app folder
  (Dropbox/Apps/SIL_SNOMED/downloads/).

2. Clone this repository:
   ```bash
   git clone git@github.com:savannahinformatics/slade360-terminology-server.git

   cd /path/to/slade360-terminology-server
   ```


3. Initialize the buildserver commands.

   This step requires that your machine can build the `cryptography` package, to make Ansible run *fast*.
   
   The `initialize.sh` script will install this, and its requirements for you.

   *NOTE* Read the recommendations below if you'd like guidance on the
   initialization process. Otherwise, the assumption is that you're
   using Ubuntu 14.04 and above as your developer OS. We also assume
   that you're using bash. Some consideration has been added for
   Darwin/Mac users. If any of these assumptions are wrong and you'd
   like to change them, or if you'd like to know what's going on, you're
   encouraged to read the [initialize.sh](./initialize.sh) script.

### Recommendations
   + Use bash. 
   + `profile completion`: Enable profile completion.
   + `rc file`: We assume that you're using bash, so `~/.bashrc` (the default option)
   + If there are network issues, just run the script again and it'll rebuild the environment.
   + Set the zone `europe`.
   + Set the region `europe-west1-d`.
   + You'll get shell autocomplete if you select it from the command line.
   + Select the gcloud project as `savannah-emr`.
   + If you add any new environment variables, you'll need to `source ~/.bashrc` or whatever .rc file handles your shell environment.
   + Any modifications to the buildserver deploy scripts will require
   you to reinitialize the package if you don't want to create your own
   virtualenv. This is because the deploy scripts are intended to run
   using a different version of python than the python3 used to run the
   whole thing, since Ansible doesn't support python 3.


   Run the initialization script to setup the buildserver dependencies.

   `./initialize.sh buildserver`
   
   *IMPORTANT NOTE*: If this command takes you to a page to create a
   google cloud account, you need to ask one of the `savannah-emr`
   project admins (either Ngure, Mutinda, Chomba, Muhia) to invite you
   to the project. *Do that before doing anything else, or everything
   after this will fail*.

4. Source the environment variables from
   [this page](https://github.com/savannahinformatics/slade360-terminology-server/wiki/Keys-and-Environment-Variables-To-Deploy-Terminology-Server).
   Put them into your shell configuration (`~/.bashrc` or `~/.zshrc`)
   and restart your shell, or `source ~/.bashrc`/`source ~/.
   
5. Create the buildserver instance.

   ```bash 
   
   cd buildserver
   build/buildserver create
   ```

   This creates a 4-core pre-emptible instance with 16GB RAM, 500GB SSD,
   optimized to be a postgresql server. This machine runs Ubuntu 14.04,
   so all software installed in it is optimized for a debian-based
   OS. There are speed/storage tradeoffs made to achieve this, which
   inform the choice to use a 500GB SSD.
   
   According to the page [https://cloud.google.com/compute/docs/disks/performance#relationship_between_size_and_performance](Optimizing Persistent Disk and Local SSD Performance: Relationship between size and performance), the VM limit for SSD Persistent Disk
   throughput is 240 MB/s for reads and 240 MB/s for writes. Generally
   speaking, larger VMs will achieve higher bandwidth.

   SSD Persistent Disk volumes reach the per-VM limit of 15000 random
   read IOPS at 333 GB. SSD Persistent Disk volumes reach the per-VM
   limit of 15000 random write IOPS at 500 GB. 
   
   We max out the read/write speeds at 500 GB, so that's the minimum for
   our purposes. This disk only lasts about an hour, every two weeks, so
   the cost is minimized.
   
   It requires full API access.

6. Deploy the buildserver.
`build/buildserver deploy`

7. `build/buildserver delete`

This buildserver machine is *very expensive* to run, so we need to
terminate it automatically every time the deploy succeeds. The machine
is also deleted automatically if the deploy fails.
