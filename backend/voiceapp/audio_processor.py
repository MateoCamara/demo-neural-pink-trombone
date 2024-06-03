import numpy as np


def process_audio(waveform, sr):
    if len(waveform.shape) == 2:
        waveform = np.mean(waveform, axis=1)

    waveform = waveform / np.max(np.abs(waveform))
    # waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)

    chunks = []

    for i in range(0, len(waveform), sr):
        chunks.append(waveform[i:i + sr])

    # es preciso asegurarse de que si no hay suficiente audio, se rellene con ceros

    for i in range(len(chunks)):
        if len(chunks[i]) < sr:
            chunks[i] = np.concatenate((chunks[i], np.zeros(sr - len(chunks[i]))))

    return chunks
