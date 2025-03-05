import os
import sqlite3
import logging

import librosa
import numpy as np
import soundfile as sf
from scipy.io import wavfile
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import init_db, get_user, insert_user
from audio_processor import detect_pitch, wsola_pitch_shift

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ling-pitch-guide')  # Secure secret key

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Allowed file types and upload limits
ALLOWED_EXTENSIONS = {"wav", "mp3", "flac"}
MAX_FILE_SIZE_MB = 10

# Ensure upload directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)


class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id)
    return User(user[0], user[1]) if user else None


# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username=username)

        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1]))
            return redirect(url_for('upload'))
        flash('Invalid credentials', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if insert_user(username, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash('Username already exists', 'error')

    return render_template('register.html')


def save_audio(filepath, audio, sr):
    """Save audio with fallback handling"""
    try:
        audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
        sf.write(filepath, audio, sr)
        logger.info(f"Audio saved using soundfile: {filepath}")
    except Exception as e:
        logger.error(f"Soundfile error: {e}. Falling back to scipy.io.wavfile.")
        try:
            wavfile.write(filepath, sr, (audio * 32767).astype(np.int16))
            logger.info(f"Audio saved using scipy: {filepath}")
        except Exception as e2:
            logger.error(f"Failed to save audio: {e2}")
            raise RuntimeError("Audio save failed")


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash("No file selected", "error")
            return redirect(request.url)

        if file.filename.rsplit('.', 1)[-1].lower() not in ALLOWED_EXTENSIONS:
            flash("Invalid file format", "error")
            return redirect(request.url)

        # Secure and save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join("uploads", filename)
        file.save(filepath)

        # Load audio
        audio, sr = librosa.load(filepath, sr=None, mono=False)

        # Detect pitch
        pitch = detect_pitch(audio, sr)

        # Get pitch shift factor (default: 1.0)
        try:
            shift_factor = float(request.form.get('shift_factor', 1.0))
        except ValueError:
            flash("Invalid pitch shift factor", "error")
            return redirect(request.url)

        # Apply pitch shifting
        shifted_audio = wsola_pitch_shift(audio, sr, shift_factor)

        # Save processed audio
        processed_filename = f"shifted_{filename.rsplit('.', 1)[0]}.wav"
        processed_filepath = os.path.join("processed", processed_filename)
        save_audio(processed_filepath, shifted_audio, sr)

        return render_template("upload.html", filename=processed_filename, pitch=f"{pitch:.2f}")

    return render_template("upload.html")


@app.route('/download/<filename>')
def download_file(filename):
    """Download processed audio file"""
    filepath = os.path.join("processed", filename)
    if not os.path.exists(filepath):
        flash("File not found", "error")
        return redirect(url_for('upload'))

    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='audio/wav')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)