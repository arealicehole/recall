import os
from flask import Flask, request, render_template_string

from src.utils.config import Config
from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber

app = Flask(__name__)
config = Config()
audio_handler = AudioHandler(config)
transcriber = Transcriber(config)

HTML_FORM = """
<!doctype html>
<title>Audio Transcriber</title>
<h1>Upload an audio file</h1>
<form method=post enctype=multipart/form-data action="/transcribe">
  <input type=file name=file required>
  <input type=submit value=Transcribe>
</form>
{% if transcript %}
<h2>Transcript</h2>
<pre>{{ transcript }}</pre>
{% endif %}
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_FORM)

@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    uploaded = request.files.get("file")
    if not uploaded:
        return render_template_string(HTML_FORM, transcript="No file uploaded")

    temp_dir = "/tmp"
    path = os.path.join(temp_dir, uploaded.filename)
    uploaded.save(path)

    prepared = audio_handler.prepare_audio(path)
    if not prepared:
        return render_template_string(HTML_FORM, transcript="Failed to process file")

    transcript_obj = transcriber.transcribe_file(prepared)
    transcript_text = transcriber.format_transcript_to_string(transcript_obj)

    audio_handler.cleanup_temp_file(prepared)
    if prepared != path and os.path.exists(path):
        os.remove(path)

    return render_template_string(HTML_FORM, transcript=transcript_text or "Transcription failed")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

