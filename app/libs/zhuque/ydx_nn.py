import os
import torch
from torch import nn
from torch.nn import functional as F


class Mnist_NN(nn.Module):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.dropout = nn.Dropout()
        self.hidden1 = nn.Linear(50, 512)
        self.hidden2 = nn.Linear(512, 256)
        self.hidden3 = nn.Linear(256, 128)
        self.out = nn.Linear(128, 5)
        self.read()

    def forward(self, x):
        x = F.relu(self.hidden1(x))
        x = self.dropout(x)
        x = F.relu(self.hidden2(x))
        x = self.dropout(x)
        x = F.relu(self.hidden3(x))
        x = self.out(x)
        return x

    def read(self):
        if os.path.exists(f"app/train_model/zqydx.pkl"):
            self.load_state_dict(torch.load(f"app/train_model/zqydx.pkl"))
