#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import time
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import whisper
import torch
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.secret_key = "whisper_video_to_text_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB limit

# Create uploads folder
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Supported video formats
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "wmv", "flv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_audio_from_video(video_path, audio_path):
    """Extracts audio from a video file"""
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
    """Transcribes audio to text using Whisper"""
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
        print("[DEBUG] Automatic language detection enabled")

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "video" not in request.files:
        flash("Video file not found")
        return redirect(request.url)

    file = request.files["video"]

    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash(
            "Unsupported file format. Please upload a video in "
            "mp4, avi, mov, mkv, wmv, or flv format."
        )
        return redirect(request.url)

    model_size = request.form.get("model_size", "base")
    language = request.form.get("language", "en")

    print(
        f"[DEBUG] Upload request received: file={file.filename}, model={model_size}, language={language}"
    )

    try:
        # Create unique filenames
        unique_id = str(uuid.uuid4())
        video_filename = f"{unique_id}_{file.filename}"
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_filename)
        audio_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}.mp3")
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}.txt")

        print(f"[DEBUG] Saving uploaded video to: {video_path}")
        # Save the video file
        file.save(video_path)
        print(
            f"[DEBUG] Video saved, size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB"
        )

        # Extract audio from video
        extract_audio_from_video(video_path, audio_path)

        # Transcribe audio to text
        transcript = transcribe_audio(audio_path, model_size, language)

        # Save text to file
        print(f"[DEBUG] Saving transcript to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"[DEBUG] Transcript saved, size: {os.path.getsize(output_path)} bytes")

        # Clean up temporary files
        print("[DEBUG] Cleaning up temporary files")
        os.remove(video_path)
        os.remove(audio_path)
        print("[DEBUG] Cleanup completed")

        return render_template(
            "result.html",
            transcript=transcript,
            output_file=os.path.basename(output_path),
        )

    except Exception as e:
        print(f"[DEBUG] Error during processing: {str(e)}")
        import traceback

        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for("index"))


@app.route("/download/<filename>")
def download_file(filename):
    return send_file(
        os.path.join(app.config["UPLOAD_FOLDER"], filename), as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
