import os
import torch
from tqdm import tqdm
from sklearn.metrics import f1_score
from pyspark.sql import SparkSession
from src.utils.config_loader import config
from src.features.graph_builder import FlightGraphBuilder
from src.models.gnn_model import FlightDelayGNN

CASSANDRA_HOST = config.get("cassandra.hosts")[0]
KEYSPACE = config.get("cassandra.keyspace")
TABLE = config.get("cassandra.table_training")
MODEL_PATH = os.path.join(
    config.get("paths.state_dir"), 
    config.get("paths.model_file")
)
EPOCHS = config.get("model.epochs")
CHECKPOINT_LOCATION = config.get("spark.checkpoint_location")[1]

def start_training():
    spark = SparkSession.builder \
        .appName("FlightDelayTraining") \
        .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    try:
        df_spark = spark.read \
            .format("org.apache.spark.sql.cassandra") \
            .options(table=TABLE, keyspace=KEYSPACE) \
            .load()
        
        count = df_spark.count()
        if count < 100:
            return
        df_pandas = df_spark.toPandas()
    
    except Exception as e:
        raise e
    finally:
        spark.stop()

    builder = FlightGraphBuilder()
    graph_data, num_nodes = builder.build_graph(df_pandas)

    device = torch.device(config.get("system.device", "cpu"))
    graph_data = graph_data.to(device)

    model = FlightDelayGNN(
        num_nodes=num_nodes,
        input_edge_feats=config.get("model.input_edge_feats", 10),
        hidden_dim=config.get("model.hidden_dim", 64),
        heads=config.get("model.heads", 2)
    ).to(device)

    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    pos_weight = torch.tensor([4.0]).to(device)
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    pbar = tqdm(range(EPOCHS), desc="Training GNN", unit="epoch")
    for epoch in pbar:
        optimizer.zero_grad()
        out = model(graph_data.x, graph_data.edge_index, graph_data.edge_attr)
        loss = criterion(out, graph_data.y)
        loss.backward()
        optimizer.step()

        preds = (torch.sigmoid(out) > 0.5).float()
        train_f1 = f1_score(graph_data.y.cpu().numpy(), preds.detach().cpu().numpy(), average='binary')

        pbar.set_postfix({
            'loss': f"{loss.item():.4f}", 
            'f1': f"{train_f1:.4f}"
        })

    torch.save(model.state_dict(), MODEL_PATH)
    print("DONE")

if __name__ == "__main__":
    start_training()