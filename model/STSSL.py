import torch
import torch.nn as nn

from STSSL_aug import (
    aug_topology, 
    aug_traffic, 
)
from STSSL_layers import (
    STEncoder, 
    SpatialHeteroModel, 
    TemporalHeteroModel, 
    MLP, 
)

class STSSL(nn.Module):
    def __init__(self, d_model, input_length, horizon, num_nodes, nmb_prototype, dropout, d_in, d_output, shm_temp, percent, batch_size, device):
        super(STSSL, self).__init__()
        self.percent = percent
        # spatial temporal encoder
        self.encoder = STEncoder(Kt=3, Ks=3, blocks=[[d_in, int(d_model//2), d_model], [d_model, int(d_model//2), d_model]], 
                        input_length=input_length, num_nodes=num_nodes, droprate=dropout)
        
        # traffic flow prediction branch (one-step prediction)
        self.mlp = MLP(d_model, d_output)
        # temporal heterogenrity modeling branch
        self.thm = TemporalHeteroModel(d_model, batch_size, num_nodes, device)
        # spatial heterogenrity modeling branch
        self.shm = SpatialHeteroModel(d_model, nmb_prototype, batch_size, shm_temp)
    
    def forward(self, view1, graph):
        # view1: [b,t,n,c]; graph: n,n 
        repr1 = self.encoder(view1, graph) 

        s_sim_mx = self.fetch_spatial_sim()
        graph2 = aug_topology(s_sim_mx, graph, percent=self.percent*2)
        
        t_sim_mx = self.fetch_temporal_sim()
        view2 = aug_traffic(t_sim_mx, view1, percent=self.percent)
        
        repr2 = self.encoder(view2, graph2)
        return repr1, repr2

    def fetch_spatial_sim(self):
        """
        Fetch the region similarity matrix generated by region embedding.
        Note this can be called only when spatial_sim is True.
        :return sim_mx: tensor, similarity matrix, (n, n)
        """
        return self.encoder.s_sim_mx.cpu()
    
    def fetch_temporal_sim(self):
        return self.encoder.t_sim_mx.cpu()

    def predict(self, z1, z2):
        '''Predicting future traffic flow.'''
        return self.mlp(z1)
    
    def temporal_loss(self, z1, z2):
        return self.thm(z1, z2)

    def spatial_loss(self, z1, z2):
        return self.shm(z1, z2)
        
    def loss(self, z1, z2):
        return self.temporal_loss(z1, z2) + self.spatial_loss(z1, z2)

def print_params(model):
    # print trainable params
    param_count = 0
    print('Trainable parameter list:')
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(name, param.shape, param.numel())
            param_count += param.numel()
    print(f'In total: {param_count} trainable parameters.')
    return

def main():
    import sys
    import argparse
    from torchsummary import summary
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=64, help="which GPU to use")
    parser.add_argument('--num_nodes', type=int, default=207, help='number of variables (e.g., 207 in METR-LA, 325 in PEMS-BAY)')
    parser.add_argument('--input_length', type=int, default=12, help='sequence length of historical observation')
    parser.add_argument('--horizon', type=int, default=12, help='sequence length of prediction')
    parser.add_argument('--input_dim', type=int, default=1, help='number of input channel')
    parser.add_argument('--output_dim', type=int, default=1, help='number of output channel')
    parser.add_argument('--d_model', type=int, default=64, help='number of hidden channel')
    parser.add_argument('--nmb_prototype', type=int, default=6, help='number of cluster')
    parser.add_argument('--dropout', type=float, default=0.2, help='drop rate')
    parser.add_argument('--shm_temp', type=float, default=0.5, help='temperature for loss of spatial heterogeneity modeling')
    parser.add_argument('--percent', type=float, default=0.1, help='augumentation percentage')
    parser.add_argument("gpu", type=int, default=3, help="which GPU to use")
    args = parser.parse_args()
    device = torch.device("cuda:{}".format(args.gpu)) if torch.cuda.is_available() else torch.device("cpu")
    model = STSSL(args.d_model, args.input_length, args.horizon, args.num_nodes, args.nmb_prototype, args.dropout, args.input_dim, args.output_dim, args.shm_temp, args.percent, 
                  args.batch_size, device).to(device)
    
    data = torch.rand(args.batch_size, args.input_length, args.num_nodes, args.input_dim).to(device)    # [b,t,n,c] 
    graph = torch.rand(args.num_nodes, args.num_nodes).to(device)    
    repr1, repr2 = model(data, graph)
    pred = model.predict(repr1, repr2)
    
    loss = model.loss(repr1, repr2)
#     summary(model, [(args.input_length, args.num_nodes, args.input_dim), (args.num_nodes, args.num_nodes)], device=device)
    print_params(model)
        
if __name__ == '__main__':
    main()
