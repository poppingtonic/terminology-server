# SNOMED CT Terminology Buildserver and API

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
- [ ] *IMPORTANT NOTE* You'll then need to get access to a Dropbox app. You'll need a
  dropbox token and a set of app keys, which you can get from one of the
  SIL technical leaders for the terminologies project (@ngurenyaga,
  @bmuhia or @bogolla).
- [ ] Copy the downloaded release ZIP files into the app folder
  (Dropbox/Apps/SIL_SNOMED/downloads/).

2. Clone this repository and checkout the `terminology-server-sandbox` branch:
   ```bash
   git clone git@github.com:savannahinformatics/slade360-terminology-server.git

   cd /path/to/slade360-terminology-server
   
   git checkout terminology-server-sandbox
   ```


3. Initialize the buildserver commands.

   This step requires that your machine can build the `cryptography` package, to make Ansible run *fast*.
   
   The `initialize.sh` script will install this, and its requirements for you.

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
`build/builderver deploy`

7. `build/buildserver delete`

This buildserver machine is *very expensive* to run, so we need to
terminate it automatically every time the deploy succeeds. The machine
is also deleted automatically if the deploy fails.
