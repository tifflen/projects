from flask import Flask, request, jsonify, send_file
from .speech import transcribe_file
from .utils import normalize_audio
from .db import init_db, save_transcript
import io
from gtts import gTTS

app = Flask(__name__)

# initialize DB
init_db()

@app.route('/', methods=['GET'])
def index():
    return jsonify({"service": "Voice-Activated Virtual Assistant", "status": "ready"})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Upload a WAV (LINEAR16) audio file with form field 'audio' to transcribe."""
    f = request.files.get('audio')
    if not f:
        return jsonify({'error': 'no audio file provided'}), 400

    tmp_orig = '/tmp/uploaded_audio.orig'
    f.save(tmp_orig)

    tmp_path = '/tmp/uploaded_audio.wav'
    try:
        normalize_audio(tmp_orig, tmp_path)
    except Exception:
        # if normalization fails, fall back to original
        tmp_path = tmp_orig

    try:
        text = transcribe_file(tmp_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    save_transcript(text, source='upload')
    return jsonify({'transcript': text})


@app.route('/transcripts', methods=['GET'])
def list_transcripts():
    from .db import list_transcripts
    rows = list_transcripts(limit=100)
    items = [{'id': r[0], 'text': r[1], 'source': r[2], 'created_at': r[3]} for r in rows]
    return jsonify({'transcripts': items})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Simple Dialogflow webhook that echoes the user's query and returns a reply."""
    req = request.get_json(silent=True)
    query_text = None
    if req:
        query_text = req.get('queryResult', {}).get('queryText')

    if not query_text:
        return jsonify({"fulfillmentText": "I didn't hear anything."})

    # Here you would implement intent handling and assistant logic
    reply = f"You said: {query_text}"
    return jsonify({"fulfillmentText": reply})


@app.route('/speak', methods=['POST'])
def speak():
    """Convert provided text to speech (MP3) using gTTS.

    Accepts form `text` or JSON `{ "text": "..." }`.
    Returns an MP3 audio response.
    """
    text = None
    if request.is_json:
        data = request.get_json(silent=True) or {}
        text = data.get('text')
    if not text:
        text = request.form.get('text')

    if not text:
        return jsonify({'error': 'no text provided'}), 400

    try:
        tts = gTTS(text)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
    except Exception as e:
        return jsonify({'error': f'TTS failed: {e}'}), 500

    save_transcript(text, source='tts')
    return send_file(buf, mimetype='audio/mpeg', as_attachment=False, download_name='speech.mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

