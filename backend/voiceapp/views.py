import os
import tempfile

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from scipy.io import wavfile

from .ia import run_model
from .audio_processor import process_audio, remove_silence
from .params_processor import process_params


@csrf_exempt
def process_voice(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')

        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_file.name)[1], delete=False) as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
            f.seek(0)

        sr, waveform = wavfile.read(f.name)

        if len(waveform.shape) == 2:
            waveform = np.mean(waveform, axis=1)

        # waveform = remove_silence(waveform, sr, vad_aggressiveness=3)

        waveform = waveform / np.max(np.abs(waveform))

        chunks = process_audio(waveform, sr)

        params = []
        last_embedding = None
        for chunk in chunks:
            computed_params, last_embedding = run_model(chunk, sr=sr, prev_embeddings=last_embedding)
            params.append(computed_params)

        final_params = process_params(params, len(chunks))

        params = {'params': final_params}

        return JsonResponse(params)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
