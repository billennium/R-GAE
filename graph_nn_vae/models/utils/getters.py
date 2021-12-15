from typing import List

import torch
from torch import optim
from torch import nn
from graph_nn_vae import lr_schedulers

from graph_nn_vae.metrics.edge_accuracy import EdgeAccuracy, MaskAccuracy
from graph_nn_vae.metrics.graph_size import MaxGraphSize
from graph_nn_vae.metrics.precision_recall import *


def get_loss(name: str, loss_weight: torch.Tensor = None):
    losses = {
        "MSE": torch.nn.MSELoss,
        "BCE": torch.nn.BCELoss,
        "BCEWithLogits": torch.nn.BCEWithLogitsLoss,
    }
    if loss_weight is not None:
        return losses[name](weight=loss_weight)
    else:
        return losses[name]()


def get_optimizer(name: str):
    optimizers = {
        "Adam": optim.Adam,
        "AdamW": optim.AdamW,
        "AdamWAMSGrad": AdamWAMSGrad,
        "SGD": optim.SGD,
    }
    return optimizers[name]


def AdamWAMSGrad(*args, **kwargs):
    return optim.AdamW(amsgrad=True, *args, **kwargs)


def get_lr_scheduler(name: str):
    optimizers = {
        "NoSched": lr_schedulers.NoSched,
        "FactorDecreasingOnMetricChange": lr_schedulers.FactorDecreasingOnMetricChange,
        "StepLR": torch.optim.lr_scheduler.StepLR,
        "MultiStepLR": torch.optim.lr_scheduler.MultiStepLR,
        "ReduceLROnPlateau": torch.optim.lr_scheduler.ReduceLROnPlateau,
    }
    return optimizers.get(name, lr_schedulers.NoSched)


def get_metrics(metrics: List[str]):
    metrics_dict = {
        "EdgeAccuracy": EdgeAccuracy,
        "MaskAccuracy": MaskAccuracy,
        "EdgePrecision": EdgePrecision,
        "EdgeRecall": EdgeRecall,
        "MaskPrecision": MaskPrecision,
        "MaskRecall": MaskRecall,
        "MaxGraphSize": MaxGraphSize,
    }
    return [metrics_dict[m]() for m in metrics]


def get_activation_function(name: str = "ReLU"):
    d = {
        "ReLU": nn.ReLU,
        "ELU": nn.ELU,
        "CELU": nn.CELU,
    }
    return d[name]
