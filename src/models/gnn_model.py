import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv, BatchNorm

class FlightDelayGNN(nn.Module):
    def __init__(self, num_nodes, input_edge_feats, hidden_dim, heads=2):
        super(FlightDelayGNN, self).__init__()
        
        self.node_emb = nn.Linear(num_nodes, hidden_dim)
        
        self.edge_proj = nn.Linear(input_edge_feats, hidden_dim)

        self.conv1 = GATv2Conv(hidden_dim, hidden_dim, heads=heads, 
                               concat=True, edge_dim=hidden_dim)
        self.bn1 = BatchNorm(hidden_dim * heads)
        
        self.conv2 = GATv2Conv(hidden_dim * heads, hidden_dim, heads=1, 
                               concat=False, edge_dim=hidden_dim)
        self.bn2 = BatchNorm(hidden_dim)

        self.decoder = nn.Sequential(
            nn.Linear(2 * hidden_dim + input_edge_feats, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x, edge_index, edge_attr):
        x = self.node_emb(x) 
        edge_attr_emb = self.edge_proj(edge_attr)
        
        x = self.conv1(x, edge_index, edge_attr=edge_attr_emb)
        x = self.bn1(x)
        x = F.elu(x)
        
        x = self.conv2(x, edge_index, edge_attr=edge_attr_emb)
        x = self.bn2(x)
        x = F.elu(x)
        
        src_idx, dst_idx = edge_index
        x_src = x[src_idx]
        x_dst = x[dst_idx]
        
        edge_cat = torch.cat([x_src, x_dst, edge_attr], dim=1)
        
        return self.decoder(edge_cat)