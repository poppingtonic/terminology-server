#!/usr/bin/env python

import os
import sys
import json
import time
import json
import click
import pkg_resources
from subprocess import call, check_call
from sarge import run, get_stdout
from six.moves import input
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient import errors
import deployment.env_variables as env_variables

buildserver_version = pkg_resources.require("snomedct-buildserver")[0].version
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

base_dir = os.path.join(app_dir, 'buildserver')

print(base_dir)

ssh_user = os.environ.get('USER', '')
private_key = os.environ.get('ANSIBLE_SSH_PRIVATE_KEY_FILE',
                             '~/.ssh/google_compute_engine')

buildserver_config_file = '{}/.buildserver_instance.json'.format(base_dir)

buildserver_playbook_file = '{}/deployment/snomedct_buildserver.yml'.format(base_dir)

from oauth2client.service_account import ServiceAccountCredentials

client_email = 'account-1@savannah-emr.iam.gserviceaccount.com'

service_account_key = env_variables.service_account_key

credentials = ServiceAccountCredentials(client_email, service_account_key,
    'https://www.googleapis.com/auth/cloud-platform')

compute = build('compute', 'v1', credentials=credentials)
project = "savannah-emr"

def _get_instance_config(key):
    """
Instance config file looks like this:
{
 'instance_name': 'foo',
 'ip_address': '130.211.100.33'
}
"""
    if os.path.isfile(buildserver_config_file):
        with open(buildserver_config_file) as f:
            instance_config = json.load(f)
        if key in ['instance_name', 'ip_address']:
            return instance_config[key]
        else:
            return None
    else:
        return None

def _fail_loudly(sarge_obj):
    """
    Throw an exit(1) error when the return code from sarge runs command is
    not zero. Delete buildserver instance to prevent resource wastage.
    """
    buildserver_exists = run('which buildserver').returncode

    os.chdir(base_dir)
    if buildserver_exists == 1:
        delete_command = '{} delete --instance-name {}'.format('build/buildserver', _get_instance_config('instance_name'))
    elif buildserver_exists == 0:
        delete_command = '{} delete --instance-name {}'.format('buildserver', _get_instance_config('instance_name'))

    if sarge_obj.returncode:
        print("Deploy failed. Deleting instance to preserve future runs.")
        run(delete_command)
        sys.exit(1)
    else:
        run(delete_command)
        print("""Build successful! The full contents of SNOMED CT UK Clinical Release \
and Drug Extension are now available on Google Cloud Storage.""")
        sys.exit(0)


def _get_default_instance_name():
    instance_name = _get_instance_config('instance_name')
    p = get_stdout('{}/commands/get_name'.format(base_dir))
    if instance_name:
        return instance_name
    else:
        print("Reticulating splines...")
        return p.strip()

def call_ansible(server, playbook, extra_vars):
    deployment_dir = os.path.join(base_dir, 'deployment')
    os.chdir(deployment_dir)

    env = {
        'ANSIBLE_CONFIG': '{}/deployment/ansible.cfg'.format(base_dir)
    }

    ansible_command = """\
ansible-playbook -i'{server},' {playbook} --extra-vars='{extra_vars}' --ask-vault-pass""".format(
    playbook=playbook,
    extra_vars=extra_vars,
    server=server.strip())

    print(ansible_command)
    p = run(ansible_command, env=env)
    _fail_loudly(p)

@click.group()
def instance():
    """Interacts with gcloud API instances to create, delete or deploy a
    build server for SNOMED CT.

    """
    pass


def create_instance(compute, name, zone, project):
    """
    Add a new instance to a gcloud project and zone.
    This instance is a custom build, with:
    - 4 cores
    - 16GB Ram
    - 500GB SSD

A list of the available source disk images can be obtained using the command:
    `gcloud compute images list --uri`
    """
    source_disk_image = \
        "projects/ubuntu-os-cloud/global/images/ubuntu-1604-xenial-v20160825"

    source_disk_type = \
        "projects/%s/zones/%s/diskTypes/pd-ssd" % (project, zone)

    machine_type = "zones/%s/machineTypes/custom-4-16384" % zone

    config = {
      'name' : name,
      'machineType' : machine_type,
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
            'diskSizeGb': 500
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

# Delete an instance

def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()


def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
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


# [START run]
@instance.command()
@click.option('--instance-name',
              help="The name of the instance to be created",
              default=_get_default_instance_name())
@click.option('--zone',
              help="The GCP zone where the machine will be hosted",
              default='europe-west1-d')
def create(instance_name, zone):
    """Creates a preemptible instance optimized for a SNOMED CT Full
build."""
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)
    project = "savannah-emr"

    print('Creating instance.')

    operation = create_instance(compute, instance_name, zone, project)
    wait_for_operation(compute, project, zone, operation['name'])

    unicode_ip = compute.instances().get(
        project=project,
        zone=zone,
        instance=instance_name
    ).execute()['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    call("gcloud compute config-ssh", shell=True)

    ip_address = str(unicode_ip)

    instance_details = {'instance_name' : instance_name,
                        'ip_address' : ip_address}

    click.echo(json.dumps(instance_details, sort_keys=True, indent=4))

    # Write instance details to configuration file.
    with open(buildserver_config_file, 'w') as f:
        f.write(json.dumps(instance_details))


@instance.command()
@click.option('--instance-name',
              help="The name of the instance to be deleted",
              default=_get_instance_config('instance_name'))
@click.option('--zone',
              help="The GCP zone where the machine is currently hosted",
              default='europe-west1-d')
def delete(instance_name, zone):
    """Deletes the currently active build server. Provide the flag
--instance-name with the short-form name of your instance, in order to
delete a machine created under another name.
    """
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)
    project = "savannah-emr"

    print('Terminating instance.')

    operation = delete_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])


@instance.command()
@click.option('--server',
              default="{}.europe-west1-d.savannah-emr".format(_get_instance_config('instance_name')),
              help="The hostname of the server you're deploying to.")
@click.option('--buildserver-version',
              help="The version of the BuildServer you'd like to deploy.",
              default=buildserver_version)
def deploy(server, buildserver_version):
    """Deploys the buildserver code and runs a full SNOMED CT build."""

    extra_vars = {
        'buildserver_version': buildserver_version,
        'ansible_ssh_user': ssh_user,
        'ansible_ssh_private_key_file': private_key,
        'pg_login_user': env_variables.login_user,
        'pg_login_password': env_variables.login_password,
        'db_user': env_variables.db_user,
        'db_pass': env_variables.db_pass,
        'db_name': env_variables.db_name,
        'ansible_host': server,
        'buildserver_secret_key': env_variables.secret_key,
        'sudo_magick_needed': 'true'
    }

    click.echo(extra_vars)
    click.echo("Deploying Terminology BuildServer version {} to \
domain {}!".format(buildserver_version, server))
    call_ansible(server, buildserver_playbook_file, json.dumps(extra_vars))


if __name__ == '__main__':
    instance()
