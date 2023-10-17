import random
import numpy as np
import pdb
import operator
import os
import sys
import time
import tqdm
import pickle
import itertools
from PIL import Image
import random
import copy

import torch
import torchvision as tv
import torch.nn as nn
import torch.autograd as autograd
import torch.nn.functional as F

from models.base_solver import BaseSolver
from models.modules import enc_net, dec_net, cnn_net, dnn_net
from models.modules import loss_fun
from utils import visualizer
from utils import metric
from models import tester
# import utils.distributed as dist

def get_solver(conf):
    return DASolver(conf)

def get_model(conf):
    return DAModel(conf)

class DASolver(BaseSolver):

    def init_tensors(self):
        pass

    def set_tensors(self, batch):
        self.tensors = {}
        for key, value in batch.items():
            if type(value) == torch.Tensor:
                self.tensors[key] = value.cuda()

    def process_batch(self, batch, phase, record=True):
        if phase == 'train':
            return self.train_batch(batch)
        elif phase == 'test':
            return self.test_batch(batch, record)
        else:
            raise ValueError('Invalid phase name!')

    def train_batch(self, batch):

        self.set_tensors(batch)
        self.net.train()

        loss, state = self.net.forward(self.tensors, 'train_G')
        self.net.zero_grad()
        self.my_backward(loss)
        self.optimizers['gen'].step()

        if self.global_step % self.print_freq == 0:
            pred_map = state['out|pred_map']
            label_map = state['out|label_map']
            self.evaluator.add_batch(label_map.view(-1).cpu().numpy(), pred_map.view(-1).cpu().numpy())
            metrics = self.evaluator.evaluate()

            for key, value in state.items():
                if key.split('|')[0] == 'scalar':
                    state[key] = value.mean().cpu().item()

            state = {**metrics, **state}

            return state

        return {}


class DAModel(nn.Module):
    def __init__(self, net_conf):
        super(MulDAModel, self).__init__()

        self.net_conf = net_conf
        self.phase = net_conf['phase'] if 'phase' in net_conf else 'train'

        self.cls_enc_net = enc_net.get_enc_net(net_conf['cls_enc_net'])
        self.cls_dec_net = dec_net.get_dec_net(net_conf['cls_dec_net'])
        self.cls_net = cnn_net.get_cnn_net(net_conf['cls_net'])

        self.mse_loss_fun = nn.MSELoss()
        self.l1_loss_fun = nn.SmoothL1Loss()
        self.cse_loss_fun = nn.CrossEntropyLoss()
        self.nll_loss_fun = nn.NLLLoss()

    def parameters_group(self):

        cls_enc_para = self.cls_enc_net.parameters()
        cls_dec_para = self.cls_dec_net.parameters()
        cls_para = self.cls_net.parameters()

        para_grp_1 = itertools.chain(cls_enc_para, cls_dec_para, cls_para)
        return {'gen': para_grp_1}

    def forward(self, tensors, phase):

        if phase == 'train_G':
            return self.forward_G(tensors)
        elif phase == 'train_D':
            return self.forward_D(tensors)
        elif phase == 'test':
            return self.inference(tensors)
        else:
            raise ValueError

    def forward_G(self, tensors):

        state = {}
        img_A1 = tensors['img_A1'] # (B, 3, H, W)
        img_A2 = tensors['img_A2'] # (B, 3, H, W)
        img_B1 = tensors['img_B1'] # (B, 3, H, W)

        label_map_A1 = tensors['label_map_A1']

        feats_A = self.reg_enc_net(img_A1) # [(B, C, h, w), ...]

        B, C, H, W = feats_A[-1].shape

        """ Loss Calculation """
        loss_total = None

        loss_w = self.net_conf['loss_weight_G']

        """ Segmentation loss """
        feats_A1_cls = self.cls_enc_net(img_A1)
        pred_map_A1 = self.cls_net(self.cls_dec_net(feats_A1_cls))

        num_classes = pred_map_A1.shape[1]

        temp_A1 = pred_map_A1.permute(0, 2, 3, 1).contiguous().view(-1, num_classes)

        loss_seg = self.cse_loss_fun(temp_A1, label_map_A1.view(-1))


        """ Total loss """
        loss_total = sum([x * loss_w[i] for i, x in enumerate([loss_seg])])

        """ save state """
        pred_map_A1 = pred_map_A1.max(dim=1)[1]
        to_cpu = lambda x: x.detach().cpu()

        state['out|pred_map'] = pred_map_A1.detach()
        state['out|label_map'] = label_map_A1.detach()
        state['scalar|loss_seg'] = loss_seg.detach()
        state['scalar|loss'] = loss_total.detach()
        state['vis|pred_maps_A1_A2B'] = [num_classes] + list(map(to_cpu, [img_A1, label_map_A1, pred_map_A1]))
        state['vis|norm_imgs_A1_A2_B_A2B_B2A'] = map(to_cpu, [img_A1, img_A2, img_B1])

        return loss_total, state

    def inference(self, tensors):

        state = {}

        img_A = tensors['img_A1'] # (B, 3, H, W)
        img_B = tensors['img_B1'] if 'img_B1' in tensors else None

        B, _, H, W = img_A.shape


        if img_B is not None:
            feats_A = self.reg_enc_net(img_A) # [(B, C, h, w), ...]
            feats_B = self.reg_enc_net(img_B) # [(B, C, h, w), ...]
            feats_A2B = cnn_net.adain_trans(feats_A[-1], feats_B[-1])
            feats_A2B = feats_A[:-1] + [feats_A2B]
            img_A2M = self.reg_net(self.reg_dec_net(feats_A2B))
            state['else|img_A2M'] = img_A2M.detach()
        else:
            img_A2M = img_A
            state['else|img_A2M'] = img_A.detach()

        if 'label_map_A1' in tensors:

            label_map_A = tensors['label_map_A1']

            feats_A = self.cls_enc_net(img_A) # [(B, C, h, w), ...]
            pred_map_A2M = self.cls_net(self.cls_dec_net(feats_A))
            num_classes = pred_map_A2M.shape[1]

            to_cpu = lambda x: x.detach().cpu()
            state['out|pred_map'] = pred_map_A2M.detach().max(dim=1)[1]
            state['out|label_map'] = label_map_A.detach()
            state['vis|pred_maps_A_A2B'] = [num_classes] + list(map(to_cpu, [img_A,
                                                                             label_map_A,
                                                                             pred_map_A2M.max(dim=1)[1]]))
        return state



