#!/bin/bash
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

echo ">>> Starting Spark..."

export SPARK_LOG_DIR="$SPARK_LOG_DIR"
export SPARK_WORKER_DIR="$SPARK_WORKER_DIR"

$SPARK_HOME/sbin/start-master.sh --webui-port 8090

$SPARK_HOME/sbin/start-worker.sh spark://$(hostname):7077 --webui-port 8091

echo "Master UI: http://localhost:8090"
echo "Worker UI: http://localhost:8091"