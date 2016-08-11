set -e
source {{termserver_install_dir}}/termserver_env.sh && source {{termserver_venv_dir}}/bin/activate && {{django_manage}} collectstatic --link --noinput --clear
