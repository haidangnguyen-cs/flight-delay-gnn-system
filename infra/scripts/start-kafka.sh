#!/bin/bash
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

echo ">>> Starting Kafka (KRaft Mode)..."

CUSTOM_CONFIG="$STATE_DIR/server.properties"

echo ">>> Generating custom configuration at $CUSTOM_CONFIG"

cp "$KAFKA_HOME/config/server.properties" "$CUSTOM_CONFIG"

sed -i "/process.roles/d" "$CUSTOM_CONFIG"
sed -i "/node.id/d" "$CUSTOM_CONFIG"
sed -i "/controller.quorum.voters/d" "$CUSTOM_CONFIG"
sed -i "/listeners/d" "$CUSTOM_CONFIG"
sed -i "/advertised.listeners/d" "$CUSTOM_CONFIG"
sed -i "/log.dirs/d" "$CUSTOM_CONFIG"

cat <<EOT >> "$CUSTOM_CONFIG"

#############################
# CUSTOM CONFIG BY START SCRIPT
#############################
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:19093

listeners=PLAINTEXT://:19092,CONTROLLER://:19093
inter.broker.listener.name=PLAINTEXT
advertised.listeners=PLAINTEXT://localhost:19092
controller.listener.names=CONTROLLER

log.dirs=$KAFKA_DATA_DIR
EOT

if [ ! -f "$KAFKA_DATA_DIR/meta.properties" ]; then
    echo ">>> Formatting Kafka storage..."
    rm -rf "$KAFKA_DATA_DIR"/*
    
    UUID=$($KAFKA_HOME/bin/kafka-storage.sh random-uuid)
    echo "Generated UUID: $UUID"
    
    $KAFKA_HOME/bin/kafka-storage.sh format -t "$UUID" -c "$CUSTOM_CONFIG" --standalone
fi

echo ">>> Starting Kafka Broker..."
nohup $KAFKA_HOME/bin/kafka-server-start.sh "$CUSTOM_CONFIG" > "$KAFKA_LOG_FILE" 2>&1 &

echo "Logs: $KAFKA_LOG_FILE"