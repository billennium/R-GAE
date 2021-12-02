from typing import List, Tuple
from argparse import ArgumentParser

import torch
from torch import nn, Tensor

from graph_nn_vae.models.utils.getters import get_activation_function
from graph_nn_vae.models.utils.calc import weighted_average
from graph_nn_vae.models.utils.layers import (
    sequential_from_layer_sizes,
    parse_layer_sizes_list,
)


class MemoryEdgeDecoder(nn.Module):
    def __init__(
        self,
        embedding_size: int,
        edge_size: int,
        decoder_hidden_layer_sizes: List[int],
        decoder_activation_function: str,
        **kwargs,
    ):
        super().__init__()
        self.embedding_size = embedding_size
        self.edge_size = edge_size

        nn_input_size = embedding_size * 2
        graph_end_mask_size = 1
        nn_output_size = embedding_size * 4 + graph_end_mask_size + edge_size

        activation_f = get_activation_function(decoder_activation_function)
        self.nn = sequential_from_layer_sizes(
            nn_input_size,
            nn_output_size,
            decoder_hidden_layer_sizes,
            activation_f,
        )

    def forward(
        self, embedding_l: Tensor, embedding_r: Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        prev_doubled_embeddings = torch.cat((embedding_l, embedding_r), dim=-1)
        nn_output = self.nn(prev_doubled_embeddings)

        (
            decoded_edges_with_mask,
            doubled_embeddings,
            mem_overwrite_ratio,
        ) = torch.split(
            nn_output,
            [
                1 + self.edge_size,
                self.embedding_size * 2,
                self.embedding_size * 2,
            ],
            dim=2,
        )

        doubled_embeddings = weighted_average(
            doubled_embeddings, prev_doubled_embeddings, mem_overwrite_ratio
        )

        new_embedding_l, new_embedding_r = torch.split(
            doubled_embeddings,
            [self.embedding_size, self.embedding_size],
            dim=-1,
        )

        return decoded_edges_with_mask, new_embedding_l, new_embedding_r

    @staticmethod
    def add_model_specific_args(parent_parser: ArgumentParser) -> ArgumentParser:
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument(
            "--decoder_hidden_layer_sizes",
            dest="decoder_hidden_layer_sizes",
            default=[256],
            type=parse_layer_sizes_list,
            metavar="DECODER_H_SIZES",
            help="list of the sizes of the decoder's hidden layers",
        )
        parser.add_argument(
            "--decoder_activation_function",
            dest="decoder_activation_function",
            default="ReLU",
            type=str,
            metavar="ACTIVATION_F_NAME",
            help="name of the activation function of hidden layers",
        )
        return parser
