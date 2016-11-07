#!/usr/bin/env bash

set -euo pipefail

# Run termserver data-fetch
fetch_snomed_full_data(){
    # Clear final_build_data directory
    mkdir -p /opt/snomedct_terminology_server/final_build_data/
    # Download files from cloud storage bucket
    for terminology_file in `gsutil ls gs://snomedct-terminology-build-data`
    do
        gsutil cp $terminology_file /opt/snomedct_terminology_server/final_build_data/ &&\
            echo "Downloaded $terminology_file" || echo "Failed to download $terminology_file"
    done
}

fetch_snomed_full_data
