#!/bin/bash

# Video to Text Converter setup script

echo "Starting Video to Text Converter Setup..."

# Check for Python
if command -v python3 &>/dev/null; then
    echo "✓ Python 3 is installed."
else
    echo "✗ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check for FFmpeg
if command -v ffmpeg &>/dev/null; then
    echo "✓ FFmpeg is installed."
else
    echo "✗ FFmpeg is not installed."
    
    # Check operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS detected. Recommended FFmpeg installation with Homebrew:"
        echo "  brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux detected. Recommended FFmpeg installation with package manager:"
        echo "  sudo apt update && sudo apt install ffmpeg   # Debian/Ubuntu"
        echo "  sudo yum install ffmpeg                      # CentOS/RHEL"
    else
        echo "You need to install FFmpeg manually:"
        echo "  https://ffmpeg.org/download.html"
    fi
    
    echo "Please run this script again after completing the FFmpeg installation."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing required libraries..."
pip install -r requirements.txt

echo "Setup completed!"
echo ""
echo "Usage:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. To use the command line interface:"
echo "   python video_to_text.py --video_path \"video_file.mp4\""
echo ""
echo "3. To use the web interface:"
echo "   python app.py"
echo "   Go to http://127.0.0.1:5000 in your browser"
echo ""
echo "4. To test:"
echo "   python test.py --video_path \"video_file.mp4\" --model_size tiny"
