#! /bin/bash

if [ $CIRCLE_NODE_INDEX == 0 ]; then
    if [ ! -d /opt/google-cloud-sdk ]; then
        curl https://sdk.cloud.google.com | bash;
        ~/google-cloud-sdk/bin/gcloud components update
    fi

    echo $GCLOUD_KEY | base64 --decode > gcloud.p12
    sudo /opt/google-cloud-sdk/bin/gcloud --quiet components update
    sudo /opt/google-cloud-sdk/bin/gcloud config set project 'savannah-emr'
    sudo /opt/google-cloud-sdk/bin/gcloud auth activate-service-account $GCLOUD_EMAIL --key-file gcloud.p12
    sudo /opt/google-cloud-sdk/bin/gcloud compute config-ssh --quiet
fi
