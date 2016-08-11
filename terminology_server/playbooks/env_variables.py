import os

login_user = os.environ.get('SIL_TERMSERVER_PG_USER',
                            'termserver_login_user')
login_password = os.environ.get('SIL_TERMSERVER_PG_PASSWORD',
                                'ready+player-one')
termserver_db_user = os.environ.get('SIL_TERMSERVER_DB_USER',
                         'snomedct_termserver_user')
termserver_db_pass = os.environ.get('SIL_TERMSERVER_DB_PASSWORD',
                         'snomedct_termserver')
termserver_db_name = os.environ.get('SIL_TERMSERVER_DB_NAME',
                         'snomedct_termserver_backend')

secret_key = os.environ.get('secret_key', '')
service_account_key = os.environ.get('SERVICE_ACCOUNT_KEY','')
newrelic_license_key = os.environ.get('SNOMED_TERMSERVER_NEWRELIC_LICENSE_KEY',
                                      '')
