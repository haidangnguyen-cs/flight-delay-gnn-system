import torch
import os
from src.utils.config_loader import config
from src.features.preprocessor import FlightPreprocessor
from src.models.gnn_model import FlightDelayGNN

class FlightPredictor:
    def __init__(self):        
        self.device = torch.device(config.get("system.device", "cpu"))
        self.preprocessor = FlightPreprocessor()
        self.model = FlightDelayGNN(
            num_nodes=self.preprocessor.num_nodes,
            input_edge_feats=config.get("model.input_edge_feats", 10),
            hidden_dim=config.get("model.hidden_dim", 64),
            heads=config.get("model.heads", 2)
        )
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_dir, config.get("paths.state_dir"), config.get("paths.model_file"))
            
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        

    def predict(self, flight_data):
        x, edge_index, edge_attr = self.preprocessor.transform(flight_data)

        if x is None:
            return None

        x = x.to(self.device)
        edge_index = edge_index.to(self.device)
        edge_attr = edge_attr.to(self.device)

        with torch.no_grad():
            logits = self.model(x, edge_index, edge_attr)
            prob = torch.sigmoid(logits).item()
            
        return prob