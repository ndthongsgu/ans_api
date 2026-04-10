import os
import uuid
from datetime import datetime
import importlib
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment

# Create audios directory if not exists
AUDIOS_DIR = Path(__file__).parent.parent / "audios"
AUDIOS_DIR.mkdir(exist_ok=True)


def generate_audio_from_text(text: str, language_code: str = "vi", return_bytes: bool = False) -> dict:
    """
    Generate audio file from text using Google Text-to-Speech
    
    Args:
        text: Text to convert to speech
        language_code: Language code (default: vi for Vietnamese)
        return_bytes: If True, returns audio_bytes instead of saving file
    
    Returns:
        dict with:
        - audio_url: URL path to saved file (if return_bytes=False)
        - audio_bytes: Binary audio data (if return_bytes=True)
        - audio_duration: Duration in seconds
        - audio_file_size: File size in bytes
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        # Generate unique filename
        audio_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.mp3"
        audio_path = AUDIOS_DIR / audio_filename
        
        # Generate audio using gTTS
        tts = gTTS(text=text, lang=language_code, slow=False)
        tts.save(str(audio_path))
        
        # Get file size
        file_size = audio_path.stat().st_size
        
        # Get duration using pydub (optional, may fail if FFmpeg not installed)
        duration_seconds = None
        try:
            audio = AudioSegment.from_mp3(str(audio_path))
            duration_seconds = len(audio) // 1000  # Convert milliseconds to seconds
        except Exception as e:
            print(f"Warning: Could not get audio duration: {str(e)}. Duration will be set to None.")
        
        if return_bytes:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            # Delete temp file
            audio_path.unlink()
            return {
                "audio_bytes": audio_bytes,
                "audio_duration": duration_seconds,
                "audio_file_size": file_size,
            }
        else:
            return {
                "audio_url": f"/audios/{audio_filename}",
                "audio_duration": duration_seconds,
                "audio_file_size": file_size,
            }
    except Exception as e:
        raise RuntimeError(f"Failed to generate audio: {str(e)}")


def delete_audio_file(audio_url: str) -> bool:
    """
    Delete audio file by its URL
    
    Args:
        audio_url: Audio URL path (e.g., /audios/filename.mp3)
    
    Returns:
        bool: True if deleted successfully
    """
    if not audio_url or not audio_url.startswith("/audios/"):
        return False
    
    try:
        filename = audio_url.split("/")[-1]
        audio_path = AUDIOS_DIR / filename
        
        if audio_path.exists():
            audio_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting audio file: {e}")
        return False
