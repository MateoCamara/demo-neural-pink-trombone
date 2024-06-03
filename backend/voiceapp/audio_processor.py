import numpy as np
import webrtcvad


def process_audio(waveform, sr):
    # waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)

    chunks = []

    for i in range(0, len(waveform), sr):
        chunks.append(waveform[i:i + sr])

    # es preciso asegurarse de que si no hay suficiente audio, se rellene con ceros

    for i in range(len(chunks)):
        if len(chunks[i]) < sr:
            chunks[i] = np.concatenate((chunks[i], np.zeros(sr - len(chunks[i]))))

    return chunks


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * frame_duration_ms / 1000)
    offset = 0
    while offset + n <= len(audio):
        yield audio[offset:offset + n]
        offset += n


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = []
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.tobytes(), sample_rate)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * num_padding_frames:
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * num_padding_frames:
                triggered = False
                ring_buffer.clear()

    voiced_audio = np.concatenate(voiced_frames)
    return voiced_audio


def remove_silence(audio, sample_rate, vad_aggressiveness=3):
    if audio.ndim > 1:
        audio = audio[:, 0]

    if audio.dtype != np.int16:
        audio = (audio * 32767).astype(np.int16)

    vad = webrtcvad.Vad(vad_aggressiveness)

    frame_duration_ms = 30
    frames = list(frame_generator(frame_duration_ms, audio, sample_rate))

    padding_duration_ms = 300
    voiced_audio = vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames)

    return voiced_audio
