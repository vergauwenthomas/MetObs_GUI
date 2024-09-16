#!/usr/bin/env bash

# This script will activate an environment to test and develop the package


echo " ----Creating envrionment ----"

DEVELOP_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${DEVELOP_DIR}
cd .. #Navigate to workdir
WORKDIR=$(pwd)



poetry install --no-root


cd ${DEVELOP_DIR}


#Now run 
# poetry run python local_launch.py 
