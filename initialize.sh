#!/usr/bin/env bash
set -euo pipefail

argerror="Please select an application to set up. Valid inputs are 'buildserver' and 'termserver'.
\n\n- buildserver If you want to build snomed from distribution files.

\n\n\n- termserver If you want to deploy the terminology server from pre-built SNOMED data.\n\n"

read -p "Which command shell do you want to  use? [bash] or zsh: "  default_shell
current_shell=${default_shell:-'bash'}

if [[ $current_shell = 'bash' ]]; then
    default_rc_file='~/.bashrc'
elif [[ $current_shell = 'zsh' ]]; then
    default_rc_file='~/.zshrc'
else
    echo -e "\n\nWe don't support any other shells, please select either 'bash' or 'zsh'."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo -e $argerror
    exit 1
fi

if [ ! -d ~/google-cloud-sdk ]; then
    sudo apt-get install -y curl
    curl https://sdk.cloud.google.com | bash;
    ~/google-cloud-sdk/bin/gcloud components update
    ~/google-cloud-sdk/bin/gcloud init
fi

gcloud compute config-ssh 1> /dev/null

if [ "$(uname)" == "Darwin" ]; then
    brew install coreutils
    alias shuf=gshuf
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo -e "\n\nInstalling libssl-dev, python-dev build-essential and postgres-plpython.\n\n" &&\
        sudo apt-get install -y libssl-dev python-dev build-essential libpq-dev postgresql-plpython-9.5
fi


app="$1"

if [[ "$app" = "termserver" ]]; then
    alias termserver='`pwd`/terminology_server/build/termserver'
    cd terminology_server && echo -e "\n\n Setting up terminology server.\n\n"
    dir=`pwd`
elif [[ "$app" = "buildserver" ]]; then
    alias buildserver='`pwd`/buildserver/build/buildserver'
    cd buildserver && echo -e "\n\n Setting up buildserver.\n\n"
    cp commands/wordlist ~/ && echo "Copying wordlist for heroku-style naming"
    dir=`pwd`
else
    echo -e "\n\nYour input '$app' is invalid.\n\n\n"
    echo -e $argerror
    exit 1
fi

virtualenv env

printf "\n\n\n\nWe need to install exec-wrappers in the global environment, so that we can set up the commands you'll use to deploy the server"
printf "\n\nInstalling exec-wrappers...\n\n\n\n\n"


sudo pip install ansible exec-wrappers && create-wrappers  -t virtualenv -b ./env/bin -d $dir/build --virtual-env-dir ./env || printf "\n\n\nYou need exec-wrapper to continue. Please re-run this script and enter your password.\n\n\n"

create-wrappers -t virtualenv -b ./env/bin -d build --virtual-env-dir ./env
build/pip install -r requirements.txt
create-wrappers -t virtualenv -b ./env/bin -d build --virtual-env-dir ./env
