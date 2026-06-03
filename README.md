# Neural Pink Trombone — demo

A small full-stack demo that drives the [Pink Trombone](https://dood.al/pinktrombone/)
articulatory voice synthesizer **from a neural network**. You record a short voice clip in
the browser, a PyTorch model predicts the matching Pink Trombone control parameters over
time, and the page re-synthesizes the voice with the Pink Trombone vocal-tract model.

## Architecture

| Part | Stack | Role |
| ---- | ----- | ---- |
| [`backend/`](backend) | Django + PyTorch | Inference service. `POST /voiceapp/process_voice/` accepts an audio file, runs it through a β-VAE synthesis model (an EnCodec-based variant is also included) and returns the smoothed, per-frame Pink Trombone parameters as JSON. |
| [`frontend/`](frontend) | JavaScript + Web Audio | A programmable Pink Trombone web page that records audio, calls the backend and plays the result back through the synthesizer. |

The backend returns `params` as 8 time series, consumed by `frontend/script/app.js` in this
order: f0, voicedness, tongue index, tongue diameter, lip diameter, constriction index,
constriction diameter, throat diameter.

## Backend setup

The trained weights are **not** included in this repository. Put your checkpoints in
`backend/models/` alongside the matching configs; by default
`backend/voiceapp/model_loader.py` loads `betavae_dynamic_1.ckpt`
(`config_betaVAESynth_dynamic_1.yaml`), with an EnCodec variant available
(`encodec_dynamic_1.ckpt`, `config_encodec_dynamic_1.yaml`).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

The model is loaded once at startup (`voiceapp/apps.py`), so the weights must be present
before the server starts. Inference runs on CUDA when available and falls back to CPU.

Optional environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (default `True`) and
`DJANGO_ALLOWED_HOSTS` (comma-separated). CORS is open by default for local development.

## Frontend setup

```bash
cd frontend
npm install
npm run build          # webpack; on recent Node you may need:
                       # NODE_OPTIONS=--openssl-legacy-provider npm run build
```

Serve the `frontend/` folder with any static server and open `index.html`. It calls the
backend at `http://localhost:8000/voiceapp/process_voice/` (edit `frontend/script/app.js` if
you host the backend elsewhere).

## Acknowledgments

- **Pink Trombone** was created by **Neil Thapen** — <https://dood.al/pinktrombone/>.
- `frontend/` is based on the programmable / refactored Pink Trombone by **zakaton**, under
  the **GPL-3.0** license (see [`frontend/LICENSE`](frontend/LICENSE) and
  [`frontend/README.md`](frontend/README.md)).
- The neural backend (the β-VAE / EnCodec synthesis models that predict the vocal-tract
  parameters) is the contribution of this repository.

## License

Released under the **GNU General Public License v3.0** — see [`LICENSE`](LICENSE). The
bundled `frontend/` keeps its original GPL-3.0 license and author attribution.
