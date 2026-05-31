from flask import Flask, request, jsonify
from speech import transcribe_file
from db import init_db, save_transcript

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

    tmp_path = '/tmp/uploaded_audio.wav'
    f.save(tmp_path)

    try:
        text = transcribe_file(tmp_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    save_transcript(text, source='upload')
    return jsonify({'transcript': text})


@app.route('/transcripts', methods=['GET'])
def list_transcripts():
    from db import list_transcripts
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
