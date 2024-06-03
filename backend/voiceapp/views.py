import io
import os
import tempfile

import librosa
import numpy as np
import torchaudio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from scipy.io import wavfile

from .ia import run_model
from .audio_processor import process_audio
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
