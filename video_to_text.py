#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import argparse
import whisper
import torch
from moviepy.editor import VideoFileClip


def extract_audio_from_video(video_path, audio_path):
    """
    Extracts audio from a video file
    """
    print(f"[DEBUG] Starting audio extraction from: {video_path}")
    video = VideoFileClip(video_path)
    print(f"[DEBUG] Video loaded. Duration: {video.duration} seconds")

    print(f"[DEBUG] Extracting audio to: {audio_path}")
    start_time = time.time()
    video.audio.write_audiofile(audio_path, verbose=False, logger=None)
    end_time = time.time()
    print(f"[DEBUG] Audio extraction completed in {end_time - start_time:.2f} seconds")

    video.close()
    return audio_path


def transcribe_audio(audio_path, model_size="base", language="en"):
    """
    Transcribes audio to text using Whisper
    """
    print(f"[DEBUG] Loading Whisper model: {model_size}")
    start_time = time.time()
    model = whisper.load_model(model_size)
    model_load_time = time.time()
    print(f"[DEBUG] Model loaded in {model_load_time - start_time:.2f} seconds")

    print(f"[DEBUG] Starting transcription with language: {language}")
    print(
        f"[DEBUG] Audio file: {audio_path}, size: {os.path.getsize(audio_path) / 1024 / 1024:.2f} MB"
    )

    # Convert 'auto' to None for automatic language detection
    detect_language = language
    if language == "auto":
        detect_language = None
        print(f"[DEBUG] Automatic language detection enabled")

    transcribe_start = time.time()
    result = model.transcribe(
        audio_path,
        language=detect_language,
        verbose=True,  # Enable verbose output
        fp16=torch.cuda.is_available(),
    )
    transcribe_end = time.time()

    print(
        f"[DEBUG] Transcription completed in {transcribe_end - transcribe_start:.2f} seconds"
    )
    print(f"[DEBUG] Detected language: {result.get('language', 'unknown')}")
    print(f"[DEBUG] Transcription result type: {type(result)}")
    print(f"[DEBUG] Transcription keys: {result.keys()}")

    # Print first 200 characters of transcription
    transcript = result["text"]
    print(f"[DEBUG] Transcription preview: {transcript[:200]}...")

    return transcript


def save_transcript(transcript, output_file):
    """
    Saves the transcription text to a file
    """
    print(f"[DEBUG] Saving transcript to: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"[DEBUG] Transcript saved, size: {os.path.getsize(output_file)} bytes")


def main():
    parser = argparse.ArgumentParser(description="Converts video file to text")
    parser.add_argument("--video_path", required=True, help="Path to the video file")
    parser.add_argument(
        "--model_size",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--output_file", default="output.txt", help="Name of the output text file"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Video language (ISO code, e.g. en, tr, fr, or 'auto' for automatic detection)",
    )

    args = parser.parse_args()

    print(f"[DEBUG] Starting video to text conversion")
    print(f"[DEBUG] Video path: {args.video_path}")
    print(f"[DEBUG] Model size: {args.model_size}")
    print(f"[DEBUG] Language: {args.language}")
    print(f"[DEBUG] Output file: {args.output_file}")

    # Create path for temporary audio file
    temp_audio_path = "temp_audio.mp3"

    try:
        # Extract audio from video
        extract_audio_from_video(args.video_path, temp_audio_path)

        # Transcribe audio to text
        transcript = transcribe_audio(temp_audio_path, args.model_size, args.language)

        # Save text to file
        save_transcript(transcript, args.output_file)

        print("[DEBUG] Process completed successfully!")

    except Exception as e:
        print(f"[DEBUG] Error during processing: {str(e)}")
        import traceback

        print(f"[DEBUG] Traceback: {traceback.format_exc()}")

    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"[DEBUG] Temporary audio file removed: {temp_audio_path}")


if __name__ == "__main__":
    main()
