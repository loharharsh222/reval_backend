import speech_recognition as sr
import tempfile
import os

class SpeechRecognizer:
    @staticmethod
    def recognize_from_file(audio_file_path):
        """
        Recognize speech from an audio file
        Returns the recognized text
        """
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise and record audio
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
                
                # Use Google's speech recognition
                text = recognizer.recognize_google(audio_data)
                return text
                
        except sr.UnknownValueError:
            return "Speech recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from speech recognition service: {e}"
        except Exception as e:
            return f"Error recognizing speech: {e}"
    
    @staticmethod
    def recognize_from_bytes(audio_bytes):
        """
        Recognize speech from audio bytes (e.g. from a POST request)
        Returns the recognized text
        """
        recognizer = sr.Recognizer()
        
        try:
            # Save the audio bytes to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Recognize speech from the temporary file
            result = SpeechRecognizer.recognize_from_file(temp_file_path)
            
            # Clean up the temporary file
            os.remove(temp_file_path)
            
            return result
            
        except Exception as e:
            return f"Error recognizing speech: {e}" 