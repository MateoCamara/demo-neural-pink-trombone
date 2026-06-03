"""Mel-spectrogram normalisation helpers (fixed dB range -> [0, 1])."""
import numpy as np


min_spec_value = -40
max_spec_value = 50

def normalizar_mel_spec(mel_spec):
    """Clip the mel spectrogram to the fixed dB range and scale it to [0, 1]."""
    mel_spec = np.clip(mel_spec, min_spec_value, max_spec_value)
    mel_spec = (mel_spec - min_spec_value) / (max_spec_value - min_spec_value)
    return mel_spec


def denormalizar_mel_spec(mel_spec):
    """Invert ``normalizar_mel_spec``, mapping [0, 1] back to the dB range."""
    mel_spec = mel_spec * (max_spec_value - min_spec_value) + min_spec_value
    return mel_spec
