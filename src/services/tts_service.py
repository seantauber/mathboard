import os
import asyncio
from openai import AsyncOpenAI
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = AsyncOpenAI(api_key=api_key)

async def generate_speech(text: str) -> str:
    """
    Generate speech from text using OpenAI's TTS API.
    Returns base64 encoded audio data.
    """
    try:
        if not text or not isinstance(text, str):
            logger.error("Invalid input text")
            return None
            
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3"
        )
        
        audio_data = response.content
        if not audio_data:
            logger.error("No audio data received from OpenAI")
            return None
            
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        return base64_audio
            
    except Exception as e:
        logger.error(f"Error in generate_speech: {str(e)}")
        return None
