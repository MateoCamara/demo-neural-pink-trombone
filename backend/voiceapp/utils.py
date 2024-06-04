import numpy as np


min_spec_value = -40
max_spec_value = 50

def normalizar_mel_spec(mel_spec):
    mel_spec = np.clip(mel_spec, min_spec_value, max_spec_value)
    mel_spec = (mel_spec - min_spec_value) / (max_spec_value - min_spec_value)
    return mel_spec


def denormalizar_mel_spec(mel_spec):
    mel_spec = mel_spec * (max_spec_value - min_spec_value) + min_spec_value
    return mel_spec