#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p $SCRIPT_DIR/../../state/logs

echo ">>> POWERING UP BIG DATA INFRASTRUCTURE <<<"

bash $SCRIPT_DIR/start-kafka.sh
bash $SCRIPT_DIR/start-cassandra.sh
bash $SCRIPT_DIR/start-spark.sh

echo ">>> ALL SYSTEMS GO! <<<"