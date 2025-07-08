#!/usr/bin/env python3

"""
Script to transcribe audio files from WhatsApp conversations to text
"""

import whisper
import os
import sys
from pathlib import Path

DEFAULT_MODEL = "base"
DEFAULT_DIR_PATH = "/Users/sebastian/dev/learning/dc-account/client-management/july"

def transcribir_audio(audio_file, model):
    """
    Translate an audio file to text using the Whisper model.
    """
    try:
        print(f"Uploading model: {model}")
        ia_model = whisper.load_model(model)
        
        result = ia_model.transcribe(audio_file, language="es")
        
        return result["text"]
        
    except Exception as e:
        print(f"Error transcribing {audio_file}: {e}")
        return None

def process_directory(directory, model):
    """
    Process a directory containing .opus audio files and transcribe them to text.
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"The directory {directory} does not exist.")
        return
    
    audio_files = list(dir_path.glob("*.opus"))
    
    if not audio_files:
        print(f"No audio files found in {directory}.")
        return
    
    for file in audio_files:
        translation = transcribir_audio(str(file), model)
        
        if translation:
            archivo_txt = file.with_suffix('.txt')
            with open(archivo_txt, 'w', encoding='utf-8') as f:
                f.write(translation)
            
            print(f"Transcription saved to {archivo_txt}")
        else:
            print(f"Error processing file {file}. No transcription was saved.")
            

def process_directories(dir_path, model):
    """
    Process all directories containing audios.
    """
    base_dir = Path(dir_path)
    
    if not base_dir.exists():
        print(f"The directory {dir_path} does not exist.")
        return
    
    chats = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("WhatsApp Chat")]
    
    print(f"Found {len(chats)} chats directories.")
    
    for chat in chats:
        process_directory(chat, model)


if __name__ == "__main__":
    target_dir = DEFAULT_DIR_PATH
    model = DEFAULT_MODEL
    
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
        model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL 
        
    process_directories(target_dir, model)