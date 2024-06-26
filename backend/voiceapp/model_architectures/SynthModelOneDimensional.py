import torch
from torch import nn
from typing import List, TypeVar
import lightning as L


Tensor = TypeVar('torch.tensor')


class SynthStage1D(L.LightningModule):
    num_iter = 0  # Variable estática global para llevar la cuenta de las iteraciones

    def __init__(self, codec_dim: int, time_dim: int, hidden_dims: List = None, output_dims: int = None,
                 beta_params: list = [], params_weight: int = 1, num_synth_params: int = 8, **kwargs):
        super().__init__()

        self.codec_dim = codec_dim
        self.time_dim = time_dim
        self.beta_params = beta_params
        self.params_weight = params_weight
        self.num_synth_params = num_synth_params

        if hidden_dims is None:
            hidden_dims = [codec_dim, codec_dim // 2, codec_dim // 4, codec_dim // 8]

        if output_dims is None:
            output_dims = 8

        if beta_params is None:
            self.beta_params = [1] * output_dims

        self.build_stage(hidden_dims=hidden_dims, output_dims=output_dims)

        self.use_previous_params_regularization = kwargs.get('use_previous_params_regularization', False)

        if self.use_previous_params_regularization:
            self.huber_delta = kwargs.get('huber_delta', 1.5)
            self.beta_previous_params = kwargs.get('beta_previous_params', [1] * num_synth_params)
            self.previous_params_weight = kwargs.get('previous_params_weight', 1.0)

    def build_stage(self, hidden_dims, output_dims):
        modules = []
        input_channel = 2
        for h_dim in hidden_dims:
            modules.append(nn.Sequential(
                nn.Conv1d(input_channel, h_dim, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                # nn.BatchNorm2d(h_dim) if h_dim != hidden_dims[0] else nn.Identity()
            ))
            input_channel = h_dim
        self.synth_stage = nn.Sequential(*modules)

        flat_size = self._calculate_output_size(self.synth_stage,
                                                torch.randn(1, 2, self.codec_dim)).numel()

        self.synth_stage_final_layer = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flat_size, flat_size // 2),
            nn.ReLU(),
            nn.Linear(flat_size // 2, self.num_synth_params),
            nn.Sigmoid()
        )

    def forward(self, input: Tensor, params: Tensor, original_audio: Tensor = None):
        x = self.synth_stage(input)
        result = self.synth_stage_final_layer(x)
        return [result, input, params, original_audio]

    def _calculate_output_size(self, model, input_tensor):
        """Calcula el tamaño de salida de un modelo dado un tensor de entrada."""
        with torch.no_grad():
            for module in model:
                input_tensor = module(input_tensor)
        return input_tensor.size()

    def print_model_summary(self):
        """
        Prints a summary of the model layers and parameters.
        """
        print("Model Summary:\n")
        total_params = 0
        for name, module in self.model.named_modules():
            # Ignoring modules that do not have learnable parameters
            if list(module.parameters(recurse=False)):
                num_params = sum(p.numel() for p in module.parameters() if p.requires_grad)
                print(f"{name} - {module.__class__.__name__} : {num_params} trainable parameters")
                total_params += num_params
        print(f"\nTotal trainable parameters: {total_params}")
