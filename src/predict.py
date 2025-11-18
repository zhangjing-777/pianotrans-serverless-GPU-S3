from piano_transcription_inference import PianoTranscription, sample_rate
import librosa
import tempfile
import os
import torch

# 全局变量，只加载一次模型
_transcriptor = None

def get_device():
    """检测并返回可用的设备"""
    if torch.cuda.is_available():
        device = 'cuda'
        print(f"CUDA available! Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        device = 'cpu'
        print("WARNING: CUDA not available, using CPU!")
    return device

def load_audio_safe(audio_path, sr=16000, mono=True):
    """安全加载音频，兼容不同版本的 librosa"""
    try:
        # 尝试使用 piano_transcription_inference 的 load_audio
        from piano_transcription_inference import load_audio
        return load_audio(audio_path, sr=sr, mono=mono)
    except (ImportError, AttributeError):
        # 降级使用 librosa
        return librosa.load(audio_path, sr=sr, mono=mono)

def get_transcriptor():
    """获取或创建转录器实例（单例模式）"""
    global _transcriptor
    if _transcriptor is None:
        device = get_device()
        print(f"Loading piano transcription model on {device}...")
        _transcriptor = PianoTranscription(device=device, checkpoint_path=None)
        print("Model loaded successfully!")
    return _transcriptor

def transcribe_piano(audio_path: str):
    """
    Load audio → run piano transcription → save MIDI
    """
    print(f"Loading audio from {audio_path}")
    
    # 加载音频
    audio, sr = load_audio_safe(audio_path, sr=sample_rate, mono=True)
    
    print(f"Audio loaded: {len(audio)} samples at {sr}Hz")
    
    # Get transcriptor (reuse if already loaded)
    transcriptor = get_transcriptor()

    # Output MIDI path
    temp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".mid")
    out_midi_path = temp_midi.name
    temp_midi.close()

    # Run inference
    print("Running transcription...")
    transcriptor.transcribe(audio, out_midi_path)
    print(f"Transcription complete, saved to {out_midi_path}")

    return out_midi_path
