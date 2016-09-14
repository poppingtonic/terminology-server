#!/usr/bin/env bash

set -euo pipefail

# Run termserver data-fetch
fetch_snomed_test_data(){
    # Clear final_build_data directory
    mkdir -p /opt/snomedct_terminology_server/final_build_data/
    # Download files from cloud storage bucket
    for terminology_file in `/opt/google-cloud-sdk/bin/gsutil ls gs://ci-snomedct-terminology-server-test-data`
    do
        /opt/google-cloud-sdk/bin/gsutil cp $terminology_file /opt/snomedct_terminology_server/final_build_data/ &&\
            echo "Downloaded $terminology_file" || echo "Failed to download $terminology_file"
    done
}

fetch_snomed_test_data
