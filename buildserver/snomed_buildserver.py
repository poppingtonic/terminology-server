#!/usr/bin/env python3
"""Create and tear down SNOMED cloud build instances."""
import os
import sys
import json
import time
import click

from six.moves import input
from subprocess import call, check_call
from sarge import run, get_stdout
from oauth2client.client import GoogleCredentials
from googleapiclient import errors
from deployment import settings
from deployment.settings import LOGGER


def _get_instance_config(key):
    """
    Retrieve the Google Cloud instance config.

    Instance config file looks like this:

    {
     'instance_name': 'foo',
     'ip_address': '130.211.100.33'
    }
    """
    if os.path.isfile(settings.BUILDSERVER_CONFIG_FILE):
        with open(settings.BUILDSERVER_CONFIG_FILE) as build_config_file:
            instance_config = json.load(build_config_file)
            if key in ["instance_name", "ip_address"]:
                return instance_config[key]

    return None


def _fail_loudly(sarge_obj):
    """
    Throw an exit(1) error when the return code from sarge runs command is
    not zero. Delete buildserver instance to prevent resource wastage.
    """
    buildserver_exists = run("which buildserver").returncode

    os.chdir(settings.BASE_DIR)
    if buildserver_exists == 1:
        delete_command = "{} delete --instance-name {}".format(
            "build/buildserver", _get_instance_config("instance_name")
        )
    elif buildserver_exists == 0:
        delete_command = "{} delete --instance-name {}".format(
            "buildserver", _get_instance_config("instance_name")
        )

    if not settings.DELETE_ON_FAILED_BUILD:
        LOGGER.debug(
            "DELETE_ON_FAILED_BUILD is set to False in settings."
            "This can cause expensive build servers to linger on."
        )

    if sarge_obj.returncode:
        if settings.DELETE_ON_FAILED_BUILD:
            LOGGER.debug(
                "Deploy failed. Deleting instance to preserve future runs."
            )
            run(delete_command)
            sys.exit(1)
    else:
        if settings.DELETE_ON_SUCCESSFUL_BUILD:
            run(delete_command)

        LOGGER.debug(
            """
            Build successful!

            The full contents of SNOMED CT UK
            Clinical Release and Drug Extension
            are now available on Google Cloud Storage."""
        )
        sys.exit(0)


def _get_default_instance_name():
    """Return an name from configuration OR a random 'heroku style' name."""
    instance_name = _get_instance_config("instance_name")
    if instance_name:
        return instance_name

    command_return_val = get_stdout(
        "{}/commands/get_name".format(settings.BASE_DIR)
    )
    return command_return_val.strip()


def call_ansible(server, playbook, extra_vars):
    """Deploy the SNOMED build server."""
    deployment_dir = os.path.join(settings.BASE_DIR, "deployment")
    os.chdir(deployment_dir)
    env = {
        "ANSIBLE_CONFIG": "{}/deployment/ansible.cfg".format(settings.BASE_DIR)
    }
    ansible_command = """
    ansible-playbook -i'{server},' {playbook} --extra-vars='{extra_vars}'
    --vault-id {home}/.vaultpass -vvvv""".format(
        playbook=playbook,
        extra_vars=extra_vars,
        server=server.strip(),
        home=settings.HOME,
    )
    LOGGER.debug(ansible_command)
    retval = run(ansible_command, env=env)
    _fail_loudly(retval)


@click.group()
def instance():
    """Group commands to create and interact with the SNOMED build instance."""
    pass


def create_instance(compute, name, zone, project):
    """
    Add a new instance to a gcloud project and zone.

    This instance is a custom build, with:

    - 4 cores
    - 16GB Ram
    - 512GB SSD

    A list of the available source disk images can be obtained using:
    `gcloud compute images list --uri`
    """
    # use an Ubuntu 18.04 base image
    source_disk_image = (
        "projects/ubuntu-os-cloud/global/images/ubuntu-1804-bionic-v20181222"
    )

    # use an SSD, for performance
    source_disk_type = "projects/%s/zones/%s/diskTypes/pd-ssd" % (
        project,
        zone,
    )

    # use a custom machine shape, with 4 cores and 16GB RAM
    machine_type = "zones/%s/machineTypes/custom-4-16384" % zone

    # custom instance config
    config = {
        "name": name,
        "machineType": machine_type,
        "scheduling": {"preemptible": True},
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_disk_image,
                    "diskType": source_disk_type,
                    "diskSizeGb": 512,
                },
            }
        ],
        "tags": {"items": ["http-server", "https-server"]},
        # Specify a network interface with NAT to access the public
        # internet.
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [
                    {"type": "ONE_TO_ONE_NAT", "name": "External NAT"}
                ],
            }
        ],
        # Allow the instance to access cloud storage and logging.
        "serviceAccounts": [
            {
                "email": "default",
                "scopes": [
                    "https://www.googleapis.com/auth/devstorage.read_write",
                    "https://www.googleapis.com/auth/logging.write",
                ],
            }
        ],
    }
    instances = compute.instances()
    LOGGER.debug(compute.instances())
    LOGGER.debug(zone)
    return instances.insert(project=project, zone=zone, body=config).execute()


def delete_instance(compute, project, zone, name):
    """Remove a Google Compute Engine instance."""
    return (
        compute.instances()
        .delete(project=project, zone=zone, instance=name)
        .execute()
    )


def wait_for_operation(compute, project, zone, operation):
    LOGGER.debug("Waiting for operation to finish...")
    while True:
        result = (
            compute.zoneOperations()
            .get(project=project, zone=zone, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            LOGGER.debug("Done.")
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)


@instance.command()
@click.option(
    "--instance-name",
    help="The name of the instance to be created",
    default=_get_default_instance_name(),
)
@click.option(
    "--zone",
    help="The GCP zone where the machine will be hosted",
    default="europe-west1-d",
)
def create(instance_name, zone):
    """Creates a preemptible instance optimized for a SNOMED CT Full build."""
    project = settings.PROJECT
    LOGGER.debug("Creating instance.")

    operation = create_instance(settings.COMPUTE, instance_name, zone, project)
    wait_for_operation(settings.COMPUTE, project, zone, operation["name"])
    unicode_ip = (
        settings.COMPUTE.instances()
        .get(project=project, zone=zone, instance=instance_name)
        .execute()["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    )

    call("gcloud compute config-ssh", shell=True)
    ip_address = str(unicode_ip)
    instance_details = {
        "instance_name": instance_name,
        "ip_address": ip_address,
    }
    click.echo(json.dumps(instance_details, sort_keys=True, indent=4))

    with open(settings.BUILDSERVER_CONFIG_FILE, "w") as config_file:
        config_file.write(json.dumps(instance_details))


@instance.command()
@click.option(
    "--instance-name",
    help="The name of the instance to be deleted",
    default=_get_instance_config("instance_name"),
)
@click.option(
    "--zone",
    help="The GCP zone where the machine is currently hosted",
    default="europe-west1-d",
)
def delete(instance_name, zone):
    """Deletes the currently active build server.

    Provide the flag --instance-name with the short-form name of your instance,
    in order to delete a machine created under another name.
    """
    LOGGER.debug("Terminating instance.")
    operation = delete_instance(
        settings.COMPUTE, settings.PROJECT, zone, instance_name
    )
    wait_for_operation(
        settings.COMPUTE, settings.PROJECT, zone, operation["name"]
    )


@instance.command()
@click.option(
    "--server",
    default="{}.europe-west1-d.savannah-emr".format(
        _get_instance_config("instance_name")
    ),
    help="The hostname of the server you're deploying to.",
)
@click.option(
    "--buildserver-version",
    help="The version of the BuildServer you'd like to deploy.",
    default=settings.BUILDSERVER_VERSION,
)
def deploy(server, buildserver_version):
    """Deploys the buildserver code and runs a full SNOMED CT build."""

    extra_vars = {
        "ansible_host": server,
        "buildserver_version": buildserver_version,
        "ansible_ssh_user": settings.SSH_USER,
        "ansible_ssh_private_key_file": settings.PRIVATE_KEY,
        "pg_login_user": settings.LOGIN_USER,
        "pg_login_password": settings.LOGIN_PASSWORD,
        "db_user": settings.DB_USER,
        "db_pass": settings.DB_PASS,
        "db_name": settings.DB_NAME,
        "buildserver_secret_key": settings.SECRET_KEY,
        "sudo_magick_needed": "true",
    }

    click.echo(extra_vars)
    click.echo(
        "Deploying Terminology BuildServer version {} to domain {}!".format(
            buildserver_version, server
        )
    )
    call_ansible(
        server, settings.BUILDSERVER_PLAYBOOK_FILE, json.dumps(extra_vars)
    )


if __name__ == "__main__":
    instance()
