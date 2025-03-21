#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is used to test if video_to_text.py is working correctly.
It tests the basic functions on a sample video file.
"""

import os
import time
import argparse
from video_to_text import extract_audio_from_video, transcribe_audio, save_transcript


def main():
    parser = argparse.ArgumentParser(
        description="Run the Video to Text conversion test"
    )
    parser.add_argument(
        "--video_path", required=True, help="Path to the video file to test"
    )
    parser.add_argument(
        "--model_size",
        default="tiny",
        help="Model size to use for testing (tiny recommended)"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Video language (ISO code, e.g. en, tr, fr, or 'auto' for automatic detection)"
    )

    args = parser.parse_args()

    print("[DEBUG] Starting Video to Text Conversion Test...")
    print(f"[DEBUG] Video to test: {args.video_path}")
    print(f"[DEBUG] Model to use: {args.model_size}")
    print(f"[DEBUG] Language: {args.language}")

    # Temporary file paths
    temp_audio_path = "test_audio.mp3"
    output_file = "test_output.txt"

    try:
        # Step 1: Extract audio from video
        print("\n[DEBUG] Step 1: Testing audio extraction...")
        start_time = time.time()
        extract_audio_from_video(args.video_path, temp_audio_path)
        extract_time = time.time() - start_time

        if os.path.exists(temp_audio_path):
            print("[DEBUG] Audio file successfully created.")
            audio_size = os.path.getsize(temp_audio_path) / (1024 * 1024)  # Size in MB
            print(f"[DEBUG] Audio file size: {audio_size:.2f} MB")
            print(f"[DEBUG] Extraction time: {extract_time:.2f} seconds")
        else:
            print("[DEBUG] Failed to create audio file!")
            return

        # Step 2: Transcribe audio to text
        print("\n[DEBUG] Step 2: Testing audio to text transcription...")
        print("[DEBUG] This process may take some time depending on the model size...")
        start_time = time.time()
        transcript = transcribe_audio(temp_audio_path, args.model_size, args.language)
        transcribe_time = time.time() - start_time

        if transcript:
            print("[DEBUG] Audio successfully transcribed to text.")
            print(f"[DEBUG] Transcription length: {len(transcript)} characters")
            print(f"[DEBUG] Transcription time: {transcribe_time:.2f} seconds")
            print(
                f"[DEBUG] Transcription sample (first 200 characters): {transcript[:200]}..."
            )

            # Print word count
            word_count = len(transcript.split())
            print(f"[DEBUG] Word count: {word_count}")

            # Print language detection info
            print(f"[DEBUG] Language specified: {args.language}")
        else:
            print("[DEBUG] Failed to transcribe audio to text!")
            return

        # Step 3: Save text to file
        print("\n[DEBUG] Step 3: Testing saving text to file...")
        save_transcript(transcript, output_file)

        if os.path.exists(output_file):
            print("[DEBUG] Transcription successfully saved to file.")
            print(f"[DEBUG] Output file: {output_file}")
            print(f"[DEBUG] Output file size: {os.path.getsize(output_file)} bytes")
        else:
            print("[DEBUG] Failed to save transcription to file!")
            return

        print("\n[DEBUG] Test completed successfully! All steps are working.")

    except Exception as e:
        print(f"\n[DEBUG] An error occurred during testing: {str(e)}")
        import traceback

        print(f"[DEBUG] Traceback: {traceback.format_exc()}")

    finally:
        # Clean up temporary files
        print("\n[DEBUG] Cleaning up temporary files...")
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"[DEBUG] {temp_audio_path} deleted.")

        # We don't delete the test output file, the user may want to examine it
        print(f"[DEBUG] Output file kept for inspection: {output_file}")


if __name__ == "__main__":
    main()
