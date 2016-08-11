set -e

cd {{install_dir}}
source {{venv_dir}}/bin/activate
source {{install_dir}}/env.sh

# Run data-fetch knowing that it'll fail on the first run
fetch_snomed_data(){
    snomed_data fetch && echo "good" ||  snomed_data fetch
}

python {{venv_dir}}/bin/manage.py db upgrade &&\
    fetch_snomed_data &&\
    load_snomed_data
