document.addEventListener('DOMContentLoaded', () => {
    const startRecordingButton = document.getElementById('start-recording');
    const playRecordingButton = document.getElementById('play-recording');
    const sendRecordingButton = document.getElementById('send-recording');
    const playInPinkTromboneButton = document.getElementById('play-in-pink-trombone');
    const playback = document.getElementById('playback');

    let recorder;
    let audioBlob;
    let isRecording = false;
    let playInPinkTromboneEventHandler;

    startRecordingButton.addEventListener('mousedown', startRecording);
    startRecordingButton.addEventListener('mouseup', stopRecording);

    document.addEventListener('keydown', (event) => {
        if (event.code === 'Space' && !isRecording) {
            event.preventDefault();
            startRecording();
        }
    });

    document.addEventListener('keyup', (event) => {
        if (event.code === 'Space' && isRecording) {
            event.preventDefault();
            stopRecording();
        }
    });

    function startRecording() {
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => {
                recorder = RecordRTC(stream, {
                    type: 'audio',
                    mimeType: 'audio/wav',
                    recorderType: StereoAudioRecorder,
                    desiredSampRate: 48000 // Puedes ajustar la tasa de muestreo según tus necesidades
                });

                recorder.startRecording();
                isRecording = true;
                startRecordingButton.textContent = 'Recording...';
            })
    }

    function stopRecording() {
        if (recorder) {
            recorder.stopRecording(() => {
                audioBlob = recorder.getBlob();
                const audioUrl = URL.createObjectURL(audioBlob);
                playback.src = audioUrl;

                document.getElementById('play-recording').style.display = 'inline-block';
                document.getElementById('send-recording').style.display = 'inline-block';
                sendRecordingButton.textContent = 'Send Recording';
                playInPinkTromboneButton.style.display = 'none';

                isRecording = false;
                startRecordingButton.textContent = 'Start Recording';

                // Para verificar la descarga
                // const downloadLink = document.createElement('a');
                // downloadLink.href = audioUrl;
                // downloadLink.download = 'recording.wav';
                // document.body.appendChild(downloadLink);
                // downloadLink.click();
                // document.body.removeChild(downloadLink);
            });
        }
    }

    playRecordingButton.addEventListener('click', () => {
        playback.play();
    });

    sendRecordingButton.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');
        sendRecordingButton.textContent = 'Sending...';


        fetch('http://localhost:8000/voiceapp/process_voice/', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                sendRecordingButton.style.display = 'none';
                playInPinkTromboneButton.style.display = 'inline-block';

                console.log(data)

                if (playInPinkTromboneEventHandler) {
                    playInPinkTromboneButton.removeEventListener('click', playInPinkTromboneEventHandler);
                }

                playInPinkTromboneEventHandler = () => {
                    playInPinkTrombone(data);
                };

                playInPinkTromboneButton.addEventListener('click', playInPinkTromboneEventHandler);

            });
    });

    function playInPinkTrombone(parameters) {
        const pinkTromboneElement = document.querySelector('pink-trombone');
        console.log(parameters)
        const freqs = parameters.params[0];
        const voicenesses = parameters.params[1];
        const tongue_indexes = parameters.params[2];
        const tongue_diams = parameters.params[3];
        const lip_diams = parameters.params[4];
        const constriction_indexes = parameters.params[5];
        const constriction_diams = parameters.params[6];
        const throat_diams = parameters.params[7];

        // Suponiendo que los parámetros incluyen frequency y otros necesarios para el pink-trombone
        pinkTromboneElement.dispatchEvent(new CustomEvent('produceSound', {
            bubbles: true,
            detail: {
                freqs: freqs,
                voicenesses: voicenesses,
                tongue_indexes: tongue_indexes,
                tongue_diams: tongue_diams,
                lip_diams: lip_diams,
                constriction_indexes: constriction_indexes,
                constriction_diams: constriction_diams,
                throat_diams: throat_diams,
                steps: 0
            }
        }));
    }
});
