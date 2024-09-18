#!/usr/bin/env bash

# This script will install all the dependencies (NOT THE PACKE FROM A BUILD!)


echo " ---- Installing Metobs Toolkit dependencies ----"

DEVELOPDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${DEVELOPDIR}
cd .. #Navigate to workdir

WORKDIR=$(pwd)
DISTDIR=${WORKDIR}/dist


poetry install --no-root #So that the GUI is taking from local and not from the build.

cd ${DEVELOPDIR} 

echo "now run: "
echo "poetry run python local_launch.py"

