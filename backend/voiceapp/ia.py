import librosa
import numpy as np
import torch
from scipy.io.wavfile import write
from scipy.signal import savgol_filter
from tqdm import tqdm
from scipy.signal import resample
from .model_loader import model_loader

# cargar el archivo de audio

bounds = [(12, 29), (2.05, 3.5), (0.6, 1.7), (20.0, 40.0), (0.5, 2), (0.5, 2.0)]


def load_audio_file(audio_path, sr):
    return librosa.load(audio_path, sr=sr)[0]


def slerp(p0, p1, t):
    """Interpola esféricamente entre dos puntos p0 y p1 usando el factor t."""
    omega = np.arccos(np.clip(np.dot(p0 / np.linalg.norm(p0), p1 / np.linalg.norm(p1)), -1, 1))
    sin_omega = np.sin(omega)
    if sin_omega == 0:
        # Co-linear points, use linear interpolation
        return (1 - t) * p0 + t * p1
    else:
        return np.sin((1.0 - t) * omega) / sin_omega * p0 + np.sin(t * omega) / sin_omega * p1


def interpolate_embeddings(embeddings, original_fps, target_fps=94):
    """Interpola los embeddings al número de pasos por segundo objetivo."""
    times_original = np.linspace(0, 1, original_fps)
    times_target = np.linspace(0, 1, target_fps)

    # Inicializa la lista de embeddings interpolados
    interpolated_embeddings = np.zeros((target_fps, embeddings.shape[1]))

    # Calcula interpolaciones para cada paso de tiempo en el objetivo
    for i in range(target_fps):
        # Encuentra los índices de los puntos originalmente más cercanos
        idx = np.searchsorted(times_original, times_target[i]) - 1
        idx_next = min(idx + 1, original_fps - 1)

        # Calcula el factor de interpolación
        t = (times_target[i] - times_original[idx]) / (times_original[idx_next] - times_original[idx])

        # Interpola esféricamente entre los dos puntos más cercanos
        interpolated_embeddings[i] = slerp(embeddings[idx], embeddings[idx_next], t)

    return interpolated_embeddings


# Calcular su frecuencia fundamental con pyin
def compute_f0(y, sr):
    return librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)


# forzar la f0 a 100 hz

def force_f0(audio, target_f0, pyin_f0, sr):
    if np.nanmean(pyin_f0) > 0:  # Evitar divisiones por cero si f0 es NaN
        stretch_factor = target_f0 / np.nanmean(pyin_f0)
    else:
        stretch_factor = 1.0

    # Cambiar la frecuencia de la señal
    return librosa.effects.pitch_shift(audio, sr=sr, n_steps=-12 * np.log2(stretch_factor))


# pasarlo por la red neuronal
def predict_parameters(model, mel_spec):
    return model.forward(input=mel_spec, params=None)


# desnormalizar los parámetros
def denormalizar_params(params):
    for i, (low, high) in enumerate(bounds):
        params[i] = params[i] * (high - low) + low
    return params


# guardar el audio
def save_audio(audio, output_path, sr):
    write(output_path, sr, audio)


# guardar los parámetros
def save_params(params, output_path):
    np.save(output_path, params)


def run_model(audio_chunk, sr, prev_embeddings=None):
    model = model_loader.model
    model_encodec = model_loader.codec_model
    device = model_loader.device

    audio_tensor = torch.as_tensor(audio_chunk).float().unsqueeze(0).unsqueeze(0).to(device)  # Add batch dimension

    embeddings = model_encodec.encode(audio_tensor)
    embeddings = embeddings[0][0]
    # Inverse process to get audio from embeddings
    arr = embeddings.to(device)
    emb = model_encodec.quantizer.decode(arr.transpose(0, 1))[0].T

    embbeding_interpolated = torch.tensor(interpolate_embeddings(emb.cpu(), original_fps=emb.shape[0], target_fps=int(
        np.round(audio_chunk.shape[0] / 512)))).float()

    last_embedding = embbeding_interpolated[-1, :]

    pyin_f0 = compute_f0(audio_chunk, sr)[0]
    try:
        nanmean = np.nanmean(pyin_f0)
    except:
        nanmean = 100
    pyin_f0 = np.nan_to_num(pyin_f0, nan=nanmean)
    pyin_f0 = resample(pyin_f0, len(embbeding_interpolated))

    pred_params = []
    for index, (mel_time_instant, pyin_time_instant) in tqdm(enumerate(zip(embbeding_interpolated, pyin_f0))):
        # input es igual al instante actual y al anterior
        if index == 0:
            if prev_embeddings is not None:
                input = torch.cat([prev_embeddings.unsqueeze(0), embbeding_interpolated[index, :].unsqueeze(0)],
                                  dim=0)
            else:
                input = torch.cat([embbeding_interpolated[index, :].unsqueeze(0)] * 2, dim=0)
        else:
            input = embbeding_interpolated[index - 1:index + 1, :]
        if input.shape[0] == 1:
            raise ValueError('Input shape is wrong')

        input = input.unsqueeze(0).to(device)
        pred_params.append(predict_parameters(model, input)[0].detach().cpu().numpy()[0])

    denorm_params = []
    for params, pyin in zip(pred_params, pyin_f0):
        aux_denorm_params = denormalizar_params(params).tolist()
        # add at the first position the f0
        aux_denorm_params.insert(0, 1)  # voiceness
        aux_denorm_params.insert(0, pyin)

        denorm_params.append(aux_denorm_params)

    denorm_params = np.array(denorm_params).T.tolist()

    filtered_params = []
    for i in range(len(denorm_params)):
        filtered_params.append(savgol_filter(denorm_params[i], window_length=32, polyorder=2).tolist())

    return denorm_params, last_embedding
