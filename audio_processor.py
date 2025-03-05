import librosa
import numpy as np
import soundfile as sf
import scipy.signal as signal


# STFT-based pitch detection
def detect_pitch(audio, sr, frame_length=2048, hop_length=512):
    # Compute Short-Time Fourier Transform
    stft = librosa.stft(audio, n_fft=frame_length, hop_length=hop_length)
    magnitude = np.abs(stft)
    
    # Find the frequency bin with maximum energy for each frame
    freqs = librosa.fft_frequencies(sr=sr, n_fft=frame_length)
    pitch = freqs[np.argmax(magnitude, axis=0)]
    
    # Average pitch across frames, ignoring zeros (silence)
    pitch = pitch[pitch > 0]
    if len(pitch) == 0:
        return 0
    return np.mean(pitch)


# WSOLA pitch shifting
def wsola_pitch_shift(audio, sr, shift_factor, frame_length=1024, hop_length=256):
    # Time-stretch factor: inverse of pitch shift factor
    stretch_factor = 1 / shift_factor
    
    # Analysis frames
    frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length).T
    output_length = int(len(audio) * stretch_factor)
    output = np.zeros(output_length)
    
    # Synthesis hop size adjusted for time scaling
    synth_hop = int(hop_length * stretch_factor)
    synth_pos = 0
    
    for frame in frames:
        if synth_pos + frame_length > output_length:
            break
        
        # Overlap-add the frame at the synthesis position
        output[synth_pos:synth_pos + frame_length] += frame * signal.windows.hann(frame_length)
        synth_pos += synth_hop
    
    # Normalize to avoid clipping
    output = output / np.max(np.abs(output) + 1e-6)
    return output