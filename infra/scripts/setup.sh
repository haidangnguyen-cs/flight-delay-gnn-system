#!/bin/bash

source "$(dirname "$0")/env.sh"

echo ">>> Starting Infrastructure Setup..."

# 1. Java Setup
if [ ! -d "$JAVA_HOME" ]; then
    echo "Downloading Java 17..."
    mkdir -p $(dirname $JAVA_HOME)
    wget -q -O java.tar.gz https://aka.ms/download-jdk/microsoft-jdk-17-linux-x64.tar.gz
    tar -xzf java.tar.gz -C $(dirname $JAVA_HOME)
    rm java.tar.gz
    echo "Java installed."
else
    echo "Java already exists. Skipping."
fi

# 2. Kafka Setup
if [ ! -d "$KAFKA_HOME" ]; then
    echo "Downloading Kafka 4.1.1..."
    mkdir -p $(dirname $KAFKA_HOME)
    wget -q -O kafka.tgz https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz
    tar -xzf kafka.tgz -C $(dirname $KAFKA_HOME)
    rm kafka.tgz
    echo "Kafka installed."
else
    echo "Kafka already exists. Skipping."
fi

# 3. Spark Setup
if [ ! -d "$SPARK_HOME" ]; then
    echo "Downloading Spark 3.5.7..."
    mkdir -p $(dirname $SPARK_HOME)
    wget -q -O spark.tgz https://downloads.apache.org/spark/spark-3.5.7-bin-hadoop3.tgz
    tar -xzf spark.tgz -C $(dirname $SPARK_HOME)
    rm spark.tgz
    echo "Spark installed."
else
    echo "Spark already exists. Skipping."
fi

# 4. Cassandra Setup
if [ ! -d "$CASSANDRA_HOME" ]; then
    echo "Downloading Cassandra 5.0.6..."
    mkdir -p $(dirname $CASSANDRA_HOME)
    wget -q -O cassandra.tar.gz https://downloads.apache.org/cassandra/5.0.6/apache-cassandra-5.0.6-bin.tar.gz
    tar -xzf cassandra.tar.gz -C $(dirname $CASSANDRA_HOME)
    rm cassandra.tar.gz
    echo "Cassandra installed."
else
    echo "Cassandra already exists. Skipping."
fi

echo ">>> Setup Complete!"