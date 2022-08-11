export SERVICE_ACCOUNT_KEY=""
export SECRET_KEY=",m"
export GOOGLE_APPLICATION_CREDENTIALS="/home/gandalf/.snomed-service-account.json"
export DATABASE_URL=postgres://snomedct_buildserver_user:snomedct_buildserver@localhost:5432/snomedct_buildserver
export APP_SETTINGS='sil_snomed_server.config.config.StagingConfig'
export MIGRATIONS_PATH=sil_snomed_server/migrations
export DROPBOX_SNOMED_FOLDER_URL=
export DROPBOX_APP_KEY=
export DROPBOX_APP_SECRET=
export DROPBOX_ACCESS_TOKEN=
alias db='python manage.py db'

