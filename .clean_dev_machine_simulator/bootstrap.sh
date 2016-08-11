set -euo pipefail

sudo apt-get update
sudo apt-get install -y git git-core python-dev build-essential libssl-dev

wget https://bootstrap.pypa.io/get-pip.py

python get-pip.py

sudo pip install virtualenv
