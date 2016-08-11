#!/usr/bin/env python3
import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from sil_snomed_server.app import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db, directory=app.config['MIGRATIONS_PATH'])
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
