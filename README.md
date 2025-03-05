# Ling Perfect Pitch Guide

A web application for pitch detection and audio processing built with Flask. The application allows users to upload audio files, detect pitch, and apply pitch shifting while maintaining duration using WSOLA (Waveform Similarity Overlap-Add) technique.

## Features

- User authentication system (register/login/logout)
- Audio file upload support (WAV, MP3, FLAC)
- Pitch detection
- Real-time pitch shifting with customizable shift factor
- Secure file handling and processing
- Processed audio file download

## Technology Stack

- **Backend**: Python, Flask
- **Authentication**: Flask-Login
- **Database**: SQLite
- **Audio Processing**:
  - librosa (audio loading and processing)
  - soundfile (audio file handling)
  - scipy (fallback audio saving)

## Setup

1. Create a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:

   ```shell
   pip install flask flask-login librosa numpy soundfile scipy werkzeug
   ```
3. Run the application and open browser at port http://localhost:5000:

   ```python
   python app.py
   ```


## File Structure

```text
ling_perfect_pitch_guide/
├── app.py               # Main application file
├── audio_processor.py   # Audio processing functions
├── db.py                # Database operations
├── static/              # Static files
├── templates/           # HTML templates
├── uploads/             # Uploaded files directory
└── processed/           # Processed files directory
```
