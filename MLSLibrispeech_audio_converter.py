# convert single file from opus to wav
# then print properties of that file

from pathlib import Path
import csv
import os
import soundfile as sf
import resampy
import librosa
import wave
import sox
import audioread


def convert_audio(audio_file: Path):
    if audio_file.exists():
        print("Exists")
    else:
        print("Does not exist")
    new_audio = Path("test_audio.wav")
    # x, s = librosa.load(audio_file)  # librosa not working, try audioread
    with audioread.audio_open(str(audio_file)) as f:
        with wave.open(new_audio, "w") as w:
            w.setnchannels(f.channels)
            w.setframerate(f.samplerate)
            w.setsampwidth(2)
            for buf in f:
                w.writeframes(buf)
   # y = resampy.resample(x, s, 16000)

    sf.write(new_audio, y, 16000, format="WAV")
    print(new_audio.name)
    if new_audio.exists():
        print("new audio exists")


audio_path = Path("test") / "audio" / "7788" / "7108" / "7788_7108_000000.opus"
convert_audio(audio_path)
