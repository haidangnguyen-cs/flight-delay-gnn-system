#!/bin/bash
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

echo ">>> Configuring Cassandra paths..."
CASS_YAML="$CASSANDRA_HOME/conf/cassandra.yaml"

sed -i "s|^data_file_directories:.*|data_file_directories:\n    - $CASSANDRA_DATA_DIR/data|g" "$CASS_YAML"
sed -i "s|^commitlog_directory:.*|commitlog_directory: $CASSANDRA_DATA_DIR/commitlog|g" "$CASS_YAML"
sed -i "s|^saved_caches_directory:.*|saved_caches_directory: $CASSANDRA_DATA_DIR/saved_caches|g" "$CASS_YAML"
sed -i "s|^hints_directory:.*|hints_directory: $CASSANDRA_DATA_DIR/hints|g" "$CASS_YAML"

sed -i "s|^cdc_enabled:.*|cdc_enabled: false|g" "$CASS_YAML"

echo ">>> Starting Cassandra..."
nohup $CASSANDRA_HOME/bin/cassandra -R > "$CASSANDRA_LOG_FILE" 2>&1 &

echo "Logs: $CASSANDRA_LOG_FILE"