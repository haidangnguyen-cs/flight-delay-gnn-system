import torch
import pandas as pd
import numpy as np
import joblib
import os
from torch_geometric.data import Data
from sklearn.preprocessing import LabelEncoder, StandardScaler
from src.utils.config_loader import config

class FlightGraphBuilder:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        state_dir = os.path.join(base_dir, config.get("paths.state_dir"))
        
        self.scaler_path = os.path.join(state_dir, config.get("paths.scaler_file"))
        self.airport_enc_path = os.path.join(state_dir, config.get("paths.airport_encoder"))
        self.carrier_enc_path = os.path.join(state_dir, config.get("paths.carrier_encoder"))

    def build_graph(self, df: pd.DataFrame):
        le_airport = LabelEncoder()
        all_airports = pd.concat([df['origin'], df['dest']]).unique()
        le_airport.fit(all_airports)
        
        df['Src_Node'] = le_airport.transform(df['origin'])
        df['Dst_Node'] = le_airport.transform(df['dest'])
        le_carrier = LabelEncoder()
        df['Carrier_ID'] = le_carrier.fit_transform(df['op_unique_carrier'])

        feature_cols = [
            'day_of_month', 'day_of_week', 'crs_minutes', 
            'distance', 'Carrier_ID', 
            'temp', 'rhum', 'prcp', 'wspd', 'coco'
        ]
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df[feature_cols])

        edge_index = torch.tensor([
            df['Src_Node'].values,
            df['Dst_Node'].values
        ], dtype=torch.long)
        
        edge_attr = torch.tensor(features_scaled, dtype=torch.float)
        
        y = torch.tensor(df['dep_del15'].values, dtype=torch.float).unsqueeze(1)

        num_nodes = len(le_airport.classes_)
        x = torch.eye(num_nodes, dtype=torch.float)

        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=y)

        joblib.dump(scaler, self.scaler_path)
        joblib.dump(le_airport, self.airport_enc_path)
        joblib.dump(le_carrier, self.carrier_enc_path)
        
        return data, num_nodes