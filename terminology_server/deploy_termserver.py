#!/usr/bin/env python

import os
import sys
import json
import time
import click
import pkg_resources
from subprocess import call
from sarge import run
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient import errors
import playbooks.env_variables as env_variables
import datetime

termserver_version = pkg_resources.require("sil-snomedct-terminology-server")[0].version
base_dir = os.path.dirname(os.path.abspath(__file__))
ssh_user = os.environ.get('USER', '')
private_key = os.environ.get('ANSIBLE_SSH_PRIVATE_KEY_FILE',
                             '~/.ssh/google_compute_engine')

today = datetime.datetime.now().date().strftime('%Y-%m-%d')

termserver_config_file = ".termserver_instance.json"


def _fail_loudly(sarge_obj):
    """
    Throw an exit(1) error when the return code from sarge runs command is
    not zero
    """
    if sarge_obj.returncode:
        sys.exit(1)


def call_ansible(server, playbook, extra_vars):
    deployment_dir = os.path.join(base_dir, 'playbooks')
    os.chdir(deployment_dir)
    ansible_command = """
ansible-playbook -i'{server},'
{playbook} --extra-vars='{extra_vars}' --tags=rebuild""".format(
        playbook=playbook,
        extra_vars=extra_vars,
        server=server.strip())
    print(ansible_command)
    p = run(ansible_command)
    _fail_loudly(p)


def run_regression_test():
    p = run('python {}'.format(
        os.path.join(base_dir,
                     'snomedct_terminology_server/server/tests/regression.py')))
    _fail_loudly(p)


def download_current_release_info():
    """Uses the gsutil command to download the current_version_info file,
and returns its contents"""
    p = run('gsutil -q cp gs://snomedct-terminology-build-data/current_version_info {}'.format(
        base_dir))
    _fail_loudly(p)
    with open('current_version_info') as f:
        return f.read().strip()


def _strip_fqdn_dot(url):
    """Naively remove the terminating dot in a fully-qualified domain name with a subdomain.
    """
    return '.'.join(url.split('.')[:3])

service_account_key = env_variables.service_account_key

credentials = GoogleCredentials.get_application_default()

compute = build('compute', 'v1', credentials=credentials)
project = "savannah-emr"

DNS_ZONE_NAME = 'slade360emr'
dns_service = build('dns', 'v1', credentials=credentials)


@click.group()
def instance():
    """Interacts with the gcloud API to create, delete or deploy a
    terminology server for SNOMED CT.

    """
    pass


def create_instance(compute, name, zone, project):
    """
    Add a new instance to a gcloud project and zone.
    This instance is a g1-small machine.
    Get a list of source disk images from: https://console.cloud.google.com/compute/images
    """

    source_disk_image = \
        "projects/ubuntu-os-cloud/global/images/ubuntu-1604-xenial-v20160610"

    source_disk_type = \
        "projects/%s/zones/%s/diskTypes/pd-ssd" % (project, zone)

    machine_type = "zones/%s/machineTypes/g1-small" % zone

    config = {
        'name': name,
        'machineType': machine_type,
        'scheduling':
        {
            'preemptible': True
        },
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                    'diskType': source_disk_type,
                    'diskSizeGb': 100
                }
            }],
        "tags": {
            "items": [
                "http-server",
                "https-server"
            ]
        },
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]
    }
    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


def delete_instance(compute, project, zone, name):
    """Delete an instance."""
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()


def create_dns_record(dns_service, project_name, managed_zone, record_name, address):
    """Create a dns record."""
    request_body = {
        "additions": [{
            "rrdatas": [
                "%s" % address
            ],
            "kind": "dns#resourceRecordSet",
            "type": "A",
            "name": "%s.slade360emr.com." % record_name,
            "ttl": 10
        }
        ]
    }

    print("Creating {}.slade360emr.com for IPv4 address: {}".format(record_name, address))
    try:
        response = dns_service.changes().create(project=project_name,
                                                managedZone=managed_zone,
                                                body=request_body).execute()
        return response
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def delete_dns_record(dns_service, project_name, managed_zone, record_name, address):
    request_body = {
        "deletions": [{
            "rrdatas": [
                "%s" % address
            ],
            "kind": "dns#resourceRecordSet",
            "type": "A",
            "name": "%s.slade360emr.com." % record_name,
            "ttl": 10
        }
        ]
    }

    try:
        print("Deleting DNS record: {}".format(record_name))
        response = dns_service.changes().create(project=project_name,
                                                managedZone=managed_zone,
                                                body=request_body).execute()
        return response
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def wait_for_operation(compute, project, zone, operation):
    print("Waiting for operation [{}] to finish...".format(operation))
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("Done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def _get_instance_config(key):
    """
Instance config file looks like this:
{'dns_record': 'snomed-20160131-release-server-2016-06-17.slade360emr.com.',
 'instance_name': 'snomedct-terminology-server',
 'ip_address': '130.211.100.33'
}
"""
    if os.path.isfile(termserver_config_file):
        with open(termserver_config_file) as f:
            instance_config = json.load(f)
        if key in ['dns_record', 'instance_name', 'ip_address']:
            return instance_config[key]
        else:
            return None
    else:
        if key == 'instance_name':
            return download_current_release_info()
        else:
            return None


# [START run]
@instance.command()
@click.option('--instance-name',
              help="The name of the instance to be created",
              default=_get_instance_config('instance_name'))
@click.option('--zone',
              help="The GCP zone where the machine will be hosted",
              default='europe-west1-d')
@click.option('--compute',
              help="The Google Compute API entry point to use",
              default=compute)
@click.option('--dns-service',
              help="The Google Cloud DNS service entry point to use",
              default=dns_service)
@click.option('--project',
              help="The GCP project that will manage the newly-created instance.",
              default=project)
@click.option('--dns-zone-name',
              help="The DNS Zone which hosts the DNS record to be created.",
              default=DNS_ZONE_NAME)
def create(instance_name, zone, compute, dns_service, project, dns_zone_name):
    """Creates a g1-small instance and attaches its IP address to a \
newly-created domain name referring to the day of the deploy. Stores the \
created instance's details in the config file: '.termserver_instance.json'.

    """
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)
    project = "savannah-emr"
    DNS_ZONE_NAME = 'slade360emr'
    dns_service = build('dns', 'v1', credentials=credentials)

    click.echo('Creating instance.')

    instance_operation = create_instance(compute, instance_name, zone, project)
    wait_for_operation(compute, project, zone, instance_operation['name'])
    call("gcloud compute config-ssh", shell=True)

    unicode_ip = compute.instances().get(
        project=project,
        zone=zone,
        instance=instance_name
    ).execute()['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    ip_address = str(unicode_ip)

    record_name = instance_name + '-' + today

    dns_record = create_dns_record(dns_service, project, DNS_ZONE_NAME, record_name, ip_address)

    instance_details = {
        'instance_name': instance_name,
        'ip_address': ip_address,
        'dns_record': dns_record['additions'][0]['name']
    }

    click.echo(json.dumps(instance_details, sort_keys=True, indent=4))

    # Write instance details to configuration file.
    with open(termserver_config_file, 'w') as f:
        f.write(json.dumps(instance_details))


@instance.command()
@click.option('--instance-name',
              help="The name of the instance to be deleted",
              default=_get_instance_config('instance_name'))
@click.option('--zone',
              help="The GCP zone where the machine is hosted",
              default='europe-west1-d')
@click.option('--compute',
              help="The Google Compute API entry point to use",
              default=compute)
@click.option('--dns-service',
              help="The Google Cloud DNS service entry point to use",
              default=dns_service)
@click.option('--project',
              help="The GCP project that hosts the instance to be deleted.",
              default=project)
@click.option('--dns-zone-name',
              help="The DNS Zone which hosts the DNS record to be deleted.",
              default=DNS_ZONE_NAME)
def delete(instance_name, zone, compute, dns_service, project, dns_zone_name):
    """Deletes a terminology server. If (by default), the server's configuration is stored on file,
this command also deletes the domain name associated with it."""

    if instance_name == _get_instance_config('instance_name'):
        record_name = _get_instance_config('dns_record').split('.')[0]

        delete_dns_record(dns_service,
                          project,
                          dns_zone_name,
                          record_name,
                          _get_instance_config('ip_address'))

    click.echo("Terminating instance: {}.".format(instance_name))

    operation = delete_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])
    call("gcloud compute config-ssh", shell=True)


@instance.command()
@click.option('--server', default=_get_instance_config('dns_record'),
              help="The hostname of the server you're deploying to.")
@click.option('--termserver-version',
              help="The version of the Terminology Server you'd like to deploy.",
              default=termserver_version)
def deploy(server, termserver_version):
    """
Deploys the SNOMED CT terminology server code. Specify the server's domain name using --server."""

    click.echo(env_variables)
    extra_vars = {
        'termserver_domain_name': _strip_fqdn_dot(server),
        'termserver_version': termserver_version,
        'ansible_ssh_user': ssh_user,
        'ansible_ssh_private_key_file': private_key,
        'pg_login_user': env_variables.login_user,
        'pg_login_password': env_variables.login_password,
        'termserver_db_user': env_variables.termserver_db_user,
        'termserver_db_pass': env_variables.termserver_db_pass,
        'termserver_db_name': env_variables.termserver_db_name,
        'ansible_host': server,
        'termserver_secret_key': env_variables.secret_key,
        'newrelic_license_key': env_variables.newrelic_license_key,
        'raven_dsn': env_variables.raven_dsn,
        'sudo_magick_needed': 'true'
    }

    click.echo(extra_vars)
    click.echo("Deploying Terminology Server version {} to domain {}!".format(
        termserver_version,
        server))

    call_ansible(server, 'snomedct_termserver.yml', json.dumps(extra_vars))
    run_regression_test()

if __name__ == '__main__':
    instance()
