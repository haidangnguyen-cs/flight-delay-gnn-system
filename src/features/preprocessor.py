import joblib
import torch
import numpy as np
import os
from src.utils.config_loader import config

class FlightPreprocessor:
    def __init__(self):
        state_dir = config.get("paths.state_dir")
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_state_dir = os.path.join(base_dir, state_dir)

        self.scaler = joblib.load(os.path.join(full_state_dir, config.get("paths.scaler_file")))
        self.le_airport = joblib.load(os.path.join(full_state_dir, config.get("paths.airport_encoder")))
        self.le_carrier = joblib.load(os.path.join(full_state_dir, config.get("paths.carrier_encoder")))
        
        self.num_nodes = len(self.le_airport.classes_)
        

    def transform(self, flight_data):
        src_node = self.le_airport.transform([flight_data['ORIGIN']])[0]
        dst_node = self.le_airport.transform([flight_data['DEST']])[0]
        carrier_id = self.le_carrier.transform([flight_data['OP_UNIQUE_CARRIER']])[0]

        raw_features = np.array([[
            flight_data['DAY_OF_MONTH'],
            flight_data['DAY_OF_WEEK'],
            flight_data['CRS_MINUTES'],
            flight_data['DISTANCE'],
            carrier_id,
            flight_data['temp'],
            flight_data['rhum'],
            flight_data['prcp'],
            flight_data['wspd'],
            flight_data['coco']
        ]])

        features_scaled = self.scaler.transform(raw_features)
        x = torch.eye(self.num_nodes)
        edge_index = torch.tensor([[src_node], [dst_node]], dtype=torch.long)
        edge_attr = torch.tensor(features_scaled, dtype=torch.float)

        return x, edge_index, edge_attr

