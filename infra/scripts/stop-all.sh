#!/bin/bash

source "$(dirname "$0")/env.sh"

echo ">>> STOPPING SERVICES..."

echo "Stopping Spark..."
$SPARK_HOME/sbin/stop-worker.sh
$SPARK_HOME/sbin/stop-master.sh

echo "Stopping Kafka..."
$KAFKA_HOME/bin/kafka-server-stop.sh

echo "Stopping Cassandra..."
pkill -f CassandraDaemon

echo ">>> Services stopped."