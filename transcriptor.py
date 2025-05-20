import speech_recognition as sr
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logger.info("Ajustando ruido ambiental...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Habla ahora...")

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            logger.info("Reconociendo...")
            text = recognizer.recognize_google(audio, language='es-ES')
            logger.info(f"Texto reconocido: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            logger.warning("No se detectó audio.")
            return None
        except sr.UnknownValueError:
            logger.warning("No se entendió lo que dijiste.")
            return None
        except sr.RequestError as e:
            logger.error(f"Error al conectar: {e}")
            return None
        except Exception as e:
            logger.error(f"Otro error: {e}")
            return None
