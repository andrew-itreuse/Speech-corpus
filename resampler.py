import librosa
import resampy
import soundfile as sf
from pathlib import Path


# general function to convert flac to wav
# looks like this isn't needed
#def flac_to_wav(flac: Path):
#    print("did this")
#    # get string for path to old and new
#    old_audio = str(flac)
#    new_audio = str(flac.parent / flac.stem) + ".wav"
#    t = Transformer()
#    t.build(old_audio, new_audio)
#    return Path(new_audio)


# more general function to resample
def deepspeech_resample(file_path: Path, destination_dir: Path):  # file_path and destination_dir should be Path objects
    try:
        # resample wav
        x, s = librosa.load(file_path)
        y = resampy.resample(x, s, 16000)
        new_audio = destination_dir / (file_path.stem + ".wav")
        sf.write(new_audio, y, 16000, format="WAV")
        return new_audio
    except Exception as e:
        print(e)
        return False


# iterate through directories in wav48
def iterate_audio(loc, dest):
    for user_dir in loc.iterdir():
        if user_dir.is_dir():
            for file in user_dir.iterdir():
                # resample
                # only use mic 1
                mic_num = file.stem.split("_")[2]
                if mic_num == "mic1":
                    deepspeech_resample(file, dest)

