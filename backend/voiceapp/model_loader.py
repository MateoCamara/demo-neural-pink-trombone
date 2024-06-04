import os

import torch
import yaml
from encodec import EncodecModel

from .model_architectures.SynthModelOneDimensional import SynthStage1D
from .model_architectures.betaModelWithSynthOneDimensional import BetaVAESynth1D





def set_weights_to_model(model, state_dict_path, device='cpu'):
    state_dict = torch.load(state_dict_path, map_location=torch.device(device))['state_dict']
    fixed_state_dict = {k.replace("model.", ""): v for k, v in state_dict.items()}
    model.load_state_dict(fixed_state_dict)
    return model


def _load_codec_model(device):
    model = EncodecModel.encodec_model_24khz()
    model.set_target_bandwidth(12.0)
    model.eval()
    model.to(device)
    return model


class ModelLoaderEncodec:
    def __init__(self):
        self.model = None
        self.codec_model = None
        self.device = 'cuda:0'
        self.config_path = 'config_encodec_dynamic_1.yaml'

        with open(f'models/{self.config_path}', 'r') as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)

    def load_models(self):
        state_dict_path = os.path.join("models/encodec_dynamic_1.ckpt")
        model = self.load_model(self.config).to(self.device)
        self.model = set_weights_to_model(model, state_dict_path, device=self.device)
        self.codec_model = _load_codec_model(self.device)

        return self.model, self.codec_model

    @staticmethod
    def load_model(config):
        return SynthStage1D(**config['model_params'], **config['exp_params'])

class ModelLoaderVAE:
    def __init__(self):
        self.model = None
        self.codec_model = None
        self.device = 'cuda:0'
        self.config_path = 'config_betaVAESynth_dynamic_1.yaml'

        with open(f'models/{self.config_path}', 'r') as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)

    def load_models(self):
        state_dict_path = os.path.join("models/betavae_dynamic_1.ckpt")
        model = self.load_model(self.config).to(self.device)
        self.model = set_weights_to_model(model, state_dict_path, device=self.device)
        return self.model

    @staticmethod
    def load_model(config):
        return BetaVAESynth1D(**config['model_params'], **config['exp_params'])

# model_loader = ModelLoaderEncodec()
model_loader = ModelLoaderVAE()
