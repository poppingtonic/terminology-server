#!/usr/bin/env bash
set -euo pipefail
built_data=`gsutil ls gs://snomedct-terminology-build-data/`

if [[ "$built_data" ]]; then
    gsutil rm gs://snomedct-terminology-build-data/*
fi

sudo chown {{deploy_user}}:{{deploy_group}} -R {{install_dir}}/final_build_data/*
gsutil cp {{install_dir}}/final_build_data/* gs://snomedct-terminology-build-data/
