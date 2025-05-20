from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
from pydub import AudioSegment
from werkzeug.utils import secure_filename
import logging
from controllers.personsHandler import PersonHandler
from transcriptor import transcribe_audio

# Explicitly set FFmpeg path
AudioSegment.converter = r"C:\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe"  # Adjust to C:\ffmpeg\ffmpeg.exe if no bin folder

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize PersonHandler
person_handler = PersonHandler()

UPLOAD_FOLDER = 'Uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        logger.error("No audio file provided")
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    webm_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    wav_path = webm_path.replace('.webm', '.wav')

    try:
        audio_file.save(webm_path)
        logger.info(f"📥 Received and saved file: {webm_path}")

        # Convert webm to wav
        try:
            audio = AudioSegment.from_file(webm_path, format="webm")
            audio.export(wav_path, format="wav")
            logger.info(f"✅ Converted to WAV: {wav_path}")
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise Exception(f"Audio conversion failed, ensure ffmpeg is installed: {str(e)}")

        # Transcribe with speech_recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='es-ES')
        logger.info(f"✅ Transcription complete: {text}")

        # Add to queue
        person = person_handler.add_person(text)
        queue = person_handler.get_queue()

        return jsonify({
            'text': text,
            'person': str(person) if person else None,
            'queue': [str(p) for p in queue]
        })

    except sr.UnknownValueError:
        logger.warning("Speech was not understood")
        return jsonify({'error': 'Could not understand the audio'}), 400
    except sr.RequestError as e:
        logger.error(f"Speech recognition error: {e}")
        return jsonify({'error': f'Speech recognition error: {e}'}), 500
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        # Cleanup
        for f in [webm_path, wav_path]:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    logger.info(f"🧹 Deleted: {f}")
            except Exception as e:
                logger.error(f"Failed to delete {f}: {str(e)}")

@app.route('/mic_transcribe', methods=['POST'])
def mic_transcribe():
    try:
        text = transcribe_audio()
        if text:
            person = person_handler.add_person(text)
            queue = person_handler.get_queue()
            return jsonify({
                'text': text,
                'person': str(person) if person else None,
                'queue': [str(p) for p in queue]
            })
        return jsonify({'error': 'No transcription available'}), 400
    except Exception as e:
        logger.error(f"Microphone transcription error: {e}")
        return jsonify({'error': f'Microphone transcription error: {e}'}), 500

@app.route('/queue', methods=['GET'])
def get_queue():
    queue = person_handler.get_queue()
    return jsonify({'queue': [str(p) for p in queue]})

if __name__ == '__main__':
    app.run(debug=True)
