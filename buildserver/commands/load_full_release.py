import click
from sil_snomed_server.app import db
from .shared.discover import enumerate_release_files
from .shared.load import load_release_files

@click.command()
def load_snomed_data():
    """Loads the newest full SNOMED UK clinical & drug release"""
    try:
        load_release_files(enumerate_release_files())
    except Exception as e:
        raise Exception("Unable to load SNOMED content: %s" % e)

if __name__ == '__main__':
    load_snomed_data()
