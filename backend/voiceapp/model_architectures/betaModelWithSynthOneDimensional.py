"""1-D beta-VAE with an auxiliary synthesis stage that predicts Pink Trombone parameters."""
import torch
from torch import nn
from typing import List, TypeVar

from .base import BaseVAE

Tensor = TypeVar('torch.tensor')


class BetaVAESynth1D(BaseVAE):
    num_iter = 0  # Global static variable to keep track of the iterations

    def __init__(self, in_channels: int, latent_dim: int, hidden_dims: List = None, beta: int = 4, beta_params: list = [],
                 num_synth_params: int = 8, hidden_dims_synth_stage: List = None, params_weight: int = 1, **kwargs):
        super().__init__()

        # Internal variable definitions
        self.latent_dim = latent_dim
        self.beta = beta
        self.num_synth_params = num_synth_params
        self.beta_params = beta_params
        self.params_weight = params_weight

        # Initialise the hidden dimensions if they are not provided
        if hidden_dims is None:
            hidden_dims = [16, 32, 64, 128]

        if hidden_dims_synth_stage is None:
            hidden_dims_synth_stage = [int(self.latent_dim / 2), int(self.latent_dim / 4), int(self.latent_dim / 8)]

        if beta_params is None:
            self.beta_params = [1] * num_synth_params

        self.build_encoder(in_channels, hidden_dims)
        self.build_synth_stage(hidden_dims_synth_stage)
        self.build_decoder(hidden_dims[::-1], 1)

        self.use_previous_params_regularization = kwargs.get('use_previous_params_regularization', False)

        if self.use_previous_params_regularization:
            self.huber_delta = kwargs.get('huber_delta', 1.5)
            self.beta_previous_params = kwargs.get('beta_previous_params', [1] * num_synth_params)
            self.previous_params_weight = kwargs.get('previous_params_weight', 1.0)

    def build_encoder(self, in_channels, hidden_dims):
        """Build the encoder part of the VAE."""
        modules = []
        for h_dim in hidden_dims:
            modules.append(nn.Sequential(
                nn.Conv1d(in_channels, out_channels=h_dim, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                # nn.BatchNorm1d(h_dim) if h_dim != hidden_dims[0] else nn.ReLU()
            ))
            in_channels = h_dim

        self.encoder = nn.Sequential(*modules)
        self.prepare_latent_variables()

    def calculate_output_size(self, model, input_tensor):
        """Compute the output size of a model for a given input tensor."""
        with torch.no_grad():
            for module in model:
                input_tensor = module(input_tensor)
        return input_tensor.size()

    def prepare_latent_variables(self):
        """Prepare the latent variables and the layers for mu and log_var."""
        self.encoder_output_size = self.calculate_output_size(self.encoder, torch.randn(1, 2, 128))
        flat_size = self.encoder_output_size.numel()
        self.encoder_output = nn.Sequential(
            nn.Flatten(),
            # nn.Dropout(0.3),
            nn.Linear(flat_size, flat_size),
            nn.ReLU(),
        )
        self.fc_mu = nn.Linear(flat_size, self.latent_dim)
        self.fc_var = nn.Linear(flat_size, self.latent_dim)

    def build_decoder(self, hidden_dims, in_channels_original):
        """Build the decoder part of the VAE."""
        self.decoder_input = nn.Sequential(
            nn.Linear(self.latent_dim, self.encoder_output_size.numel()),
            nn.ReLU(),
        )
        modules = []
        for i, h_dim in enumerate(hidden_dims):
            modules.append(nn.Sequential(
                nn.ConvTranspose1d(in_channels=h_dim, out_channels=hidden_dims[i + 1] if i + 1 < len(
                    hidden_dims) else in_channels_original,
                                   kernel_size=3, stride=1, padding=1,),
                                   # output_padding=1 if i != len(hidden_dims) - 2 else (1, 0)),
                nn.ReLU() if h_dim != hidden_dims[-1] else nn.Sigmoid(),
                # nn.BatchNorm1d(hidden_dims[i + 1]) if i + 1 < len(hidden_dims) else nn.Identity()
            ))
        self.decoder = nn.Sequential(*modules)

    def build_synth_stage(self, hidden_dims):
        modules = []
        input_channel = self.latent_dim
        for h_dim in hidden_dims:
            modules.append(nn.Sequential(
                nn.Linear(input_channel, h_dim),
                nn.ReLU())
            )
            input_channel = h_dim
        self.synth_stage = nn.Sequential(*modules)

        self.synth_stage_final_layer = nn.Sequential(
            nn.Linear(hidden_dims[-1], self.num_synth_params),
            nn.Sigmoid()
        )

    def encode(self, input: Tensor):
        """Encode the input and return the latent codes."""
        result = self.encoder(input)
        result = self.encoder_output(result)
        mu = self.fc_mu(result)
        log_var = self.fc_var(result)
        return [mu, log_var]

    def latent_to_params(self, z: Tensor):
        """Convert the latent codes into the synthesised parameters."""
        return self.synth_stage_final_layer(self.synth_stage(z))

    def decode(self, z: Tensor):
        """Decode the latent codes into the input reconstruction."""
        z = self.decoder_input(z)
        z = z.view(-1, self.encoder_output_size[1], self.encoder_output_size[2])
        result = self.decoder(z)
        return result

    def reparameterize(self, mu: Tensor, logvar: Tensor):
        """Reparameterisation trick to obtain z."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return eps.mul(std).add_(mu)

    def forward(self, input: Tensor, params: Tensor, **kwargs):
        """Forward pass of the model."""
        mu, log_var = self.encode(input)
        z = self.reparameterize(mu, log_var)
        return [self.decode(z), input, mu, log_var, self.latent_to_params(z), params]
