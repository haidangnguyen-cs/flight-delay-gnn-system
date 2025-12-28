#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

export STATE_DIR="$PROJECT_ROOT/state"
mkdir -p "$STATE_DIR"

export JAVA_HOME=$PROJECT_ROOT/infra/java/jdk-17.0.17+10

# --- KAFKA CONFIG ---
export KAFKA_HOME="$PROJECT_ROOT/infra/kafka/kafka_2.13-4.1.1"
export KAFKA_DATA_DIR="$STATE_DIR/kafka"
export KAFKA_LOG_FILE="$STATE_DIR/logs/kafka.log"

# --- CASSANDRA CONFIG ---
export CASSANDRA_HOME="$PROJECT_ROOT/infra/cassandra/apache-cassandra-5.0.6"
export CASSANDRA_DATA_DIR="$STATE_DIR/cassandra"
export CASSANDRA_LOG_FILE="$STATE_DIR/logs/cassandra.log"

# --- SPARK CONFIG ---
export SPARK_HOME="$PROJECT_ROOT/infra/spark/spark-3.5.7-bin-hadoop3"
export SPARK_WORKER_DIR="$STATE_DIR/spark/work"
export SPARK_LOG_DIR="$STATE_DIR/spark/logs"

mkdir -p "$STATE_DIR/logs"
mkdir -p "$KAFKA_DATA_DIR"
mkdir -p "$CASSANDRA_DATA_DIR"
mkdir -p "$SPARK_WORKER_DIR"
mkdir -p "$SPARK_LOG_DIR"

echo ">>> STATE DIR SET TO: $STATE_DIR"