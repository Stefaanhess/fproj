import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import time
from Code.DataGeneration.saver import create_path
from Code.Models.base_model import BaseNet


class DeepPotential(BaseNet):

    def __init__(self, use_cuda, checkpoint_path, arch=None):
        super(DeepPotential, self).__init__(use_cuda,
                                            checkpoint_path,
                                            arch)

    def _setup(self):
        # one subnetwork for every layer:
        sub_dim = 18 * 4
        for subnetwork in ['h_net', 'o_net', 'c_net']:
            setattr(self, subnetwork, nn.Sequential(nn.Linear(sub_dim, 80),
                                                    #nn.ReLU(),
                                                    #nn.BatchNorm1d(600),
                                                    #nn.Linear(600, 400),
                                                    #nn.ReLU(),
                                                    #nn.BatchNorm1d(400),
                                                    #nn.Linear(400, 200),
                                                    #nn.ReLU(),
                                                    #nn.BatchNorm1d(200),
                                                    #nn.Linear(200, 100),
                                                    #nn.ReLU(),
                                                    #nn.BatchNorm1d(100),
                                                    #nn.Linear(100, 80),
                                                    nn.ReLU(),
                                                    nn.BatchNorm1d(80),
                                                    nn.Linear(80, 40),
                                                    nn.ReLU(),
                                                    nn.BatchNorm1d(40),
                                                    nn.Linear(40, 20),
                                                    nn.ReLU(),
                                                    nn.BatchNorm1d(20),
                                                    nn.Linear(20, 10),
                                                    nn.ReLU(),
                                                    nn.BatchNorm1d(10),
                                                    nn.Linear(10, 1),
                                                    nn.ReLU()))
            
    def forward(self, X):
        a1 = self.h_net(X[:, 0])
        a2 = self.h_net(X[:, 1])
        a3 = self.h_net(X[:, 2])
        a4 = self.h_net(X[:, 3])
        a5 = self.h_net(X[:, 4])
        a6 = self.h_net(X[:, 5])
        a7 = self.h_net(X[:, 6])
        a8 = self.h_net(X[:, 7])
        a9 = self.h_net(X[:, 8])
        a10 = self.h_net(X[:, 9])
        a11 = self.c_net(X[:, 10])
        a12 = self.c_net(X[:, 11])
        a13 = self.c_net(X[:, 12])
        a14 = self.c_net(X[:, 13])
        a15 = self.c_net(X[:, 14])
        a16 = self.c_net(X[:, 15])
        a17 = self.c_net(X[:, 16])
        a18 = self.o_net(X[:, 17])
        a19 = self.o_net(X[:, 18])
        out = a1 + a2 + a3 + a4 + a5 + a6 \
                + a7 + a8 + a9 + a10 + a11 \
              + a12 + a13 + a14 + a15 + a16 \
              + a17 + a18 + a19
        return out



def normalize(Y):
    Y_min = Y.min()
    Y_max = Y.max()
    return (Y - Y_min) / (Y_max - Y_min), Y_min, Y_max

def backtransform(Y_normed, Y_min, Y_max):
    return Y_normed * (Y_max - Y_min) + Y_min










#####################################################################
# old
#####################################################################

class OLD_SubNetwork(nn.Module):
    def __init__(self, input_dim):
        # 600-400-200-100-80-40-20
        super(SubNetwork, self).__init__()
        self.h1 = nn.Linear(input_dim, 600)
        self.h1_bn = nn.BatchNorm1d(600)
        self.h2 = nn.Linear(600, 400)
        self.h2_bn = nn.BatchNorm1d(400)
        self.h3 = nn.Linear(400, 200)
        self.h3_bn = nn.BatchNorm1d(200)
        self.h4 = nn.Linear(200, 100)
        self.h4_bn = nn.BatchNorm1d(100)
        self.h5 = nn.Linear(100, 80)
        self.h5_bn = nn.BatchNorm1d(80)
        self.h6 = nn.Linear(80, 40)
        self.h6_bn = nn.BatchNorm1d(40)
        self.h7 = nn.Linear(40, 20)
        self.h7_bn = nn.BatchNorm1d(20)
        self.h8 = nn.Linear(20, 1)

    def forward(self, X):
        a1 = F.relu(self.h1_bn(self.h1(X)))
        a2 = F.relu(self.h2_bn(self.h2(a1)))
        a3 = F.relu(self.h3_bn(self.h3(a2)))
        a4 = F.relu(self.h4_bn(self.h4(a3)))
        a5 = F.relu(self.h5_bn(self.h5(a4)))
        a6 = F.relu(self.h6_bn(self.h6(a5)))
        a7 = F.relu(self.h7_bn(self.h7(a6)))
        out = self.h8(a7)
        return out


def old_train(model, optim, scheduler, X_train, Y_train, X_test, Y_test, n_epochs, batchsize, use_for_train=0.8, print_every=100, n_calc_test=100,
          checkpoint_path='ModelCheckpoints/', shuffle=False):
    # empty lists to store data for plotting
    epochs = []
    losses = []
    tests = []
    time_per_loop = []
    # Create path for storing checkpoints:
    create_path(checkpoint_path)
    # time measurements
    start_time = time.time()
    total_time = time.time()
    # loss funtion
    loss_fn = nn.MSELoss()

    n_batches = X_train.shape[0] // batchsize
    data_ids = np.arange(X_train.shape[0])
    for epoch in range(n_epochs):
        if shuffle:
            np.random.shuffle(data_ids)
        for batch_id in range(n_batches - 1):
            # forward pass
            batch_indices = data_ids[batch_id * batchsize:(batch_id + 1) * batchsize]
            X_batch = X_train[batch_indices]
            Y_batch = Y_train[batch_indices]
            Y_pred = model.forward(X_batch)
            Y_pred = Y_pred.reshape(Y_pred.shape[0])
            loss = loss_fn(Y_pred, Y_batch)
            # update parameters
            optim.zero_grad()
            loss.backward()
            optim.step()
            # for plots
            losses.append(loss.item())

            # prints
            if batch_id % print_every == 0 and batch_id != 0:
                total_duration = time.time() - total_time
                mean_loss = np.round(np.mean(losses[-print_every:]), 6)
                total_iterations = n_epochs * n_batches
                done = epoch * n_batches + batch_id
                to_do = total_iterations - done
                av_itertime = total_duration / done
                time_estimate = av_itertime * to_do
                progress = done / total_iterations
                output_string = 'total: {} %\tcurrent epoch: {} %\tloss: {}\ttime estimate: {} min'.format(
                    np.round(progress * 100, 1),
                    np.round(batch_id / n_batches * 100, 1),
                    mean_loss,
                    np.round(time_estimate / 60, 1))
                print(output_string)
                with open("logfile.txt", "a") as log_file:
                    print(output_string, file=log_file)
                time_per_loop.append(av_itertime)

        checkpoint_file = checkpoint_path + 'epoch_{}'.format(epoch)
        torch.save(model.state_dict(), checkpoint_file)
        print('saved checkpoint at: {}\n'.format(checkpoint_file))
        # update learning rate
        scheduler.step()

    return model, optim

