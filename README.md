# SNOMED CT Terminology Buildserver and API
This repository hosts the SIL SNOMED buildserver.

The `buildserver` project runs a full build of the SNOMED CT release files
downloaded from the Technology Reference data Update Distribution site:
[Clinical](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26/subpack/102/releases)
and
[Drugs](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26/subpack/106/releases).

These files are two zipfiles containing the International clinical release
files and UK clinical extension files, and the UK drug extension.

The end result is a list of compressed files, stored in the Google Cloud
Storage bucket:
[snomedct-terminology-build-data](https://console.cloud.google.com/storage/browser/snomedct-terminology-build-data/?project=savannah-emr).

We should build SNOMED every two weeks, to follow the release schedule of the
UK drug extension.

## How To Build SNOMED

1. SNOMED CT is released on a rolling schedule of six months for
clinical releases, and two weeks for drug releases in the UK. Since we
rely on the terminology files released by the UK's National Health
Service, we will track the UK's release schedule.

The
[Technology Reference data Update Distribution site](https://isd.hscic.gov.uk/trud3/user/authenticated/group/2/pack/26)
hosts the release files, and you should go to that url to download the
release files.

- [ ] Look for 'UK SNOMED CT Drug Extension, RF2: Full' and click
  'Download releases'

- [ ] Look for 'UK SNOMED CT Clinical Edition, RF2: Full' and click
  'Download releases'

- [ ] *IMPORTANT NOTE* You'll then need to get access to a Dropbox
  app. You'll need a DropBox token and a set of app keys, which are in
  an ansible vault. Check the project's wiki for a password to the
  ansible vault.

- [ ] Check the app folder (Dropbox/Apps/SNOMED/downloads/) for any
  existing release packages. Delete any packages in there before you add
  anything new.

- [ ] Copy the downloaded release ZIP files into the app folder
  (Dropbox/Apps/SNOMED/downloads/).

2. Clone this repository:

3. Initialize the buildserver commands.

   This step requires that your machine can build the `cryptography` package,
   to make Ansible run *fast*.

   The `initialize.sh` script will install this, and its requirements for you.

   *NOTE* Read the recommendations below if you'd like guidance on the
   initialization process. Otherwise, the assumption is that you're
   using Ubuntu 18.04 and above as your developer OS. We also assume
   that you're using bash.

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
   project admins to invite you to the project. *Do that before doing anything else, or everything
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
   optimized to be a postgresql server. This machine runs Ubuntu 18.04,
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
