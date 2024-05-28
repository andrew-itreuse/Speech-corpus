# this will take one of my generated csv files, and downsample every audio file listed to 16kHz
# may not work for all file types, more research needed on that
# should definitely work for wav and flac
# soundfile does not support mp3, this has been bypassed by converting from mp3 to wav first
from pathlib import Path
import csv
import os
import soundfile as sf
import resampy
import librosa
import wave
from pydub import AudioSegment


# more general function to resample
def deepspeech_resample(file_path: Path, destination_dir: Path):  # file_path and destination_dir should be Path objects
    # handles mp3 differently
    if file_path.suffix == ".mp3":
        try:
            new_audio = ffmpeg_mp3_to_wav(file_path, destination_dir)
            return new_audio
        except Exception as e:
            print(e)
            return False
    else:
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


def ffmpeg_mp3_to_wav(file: Path, dest_dir: Path):
    sound = AudioSegment.from_mp3(str(file))
    # write new wav file
    new_wav = dest_dir / (file.stem + ".wav")
    sound.export(str(new_wav), format="wav")
    # now read and resample it
    x, s = librosa.load(new_wav)
    res_audio = resampy.resample(x, s, 16000)
    sf.write(new_wav, res_audio, 16000, format="WAV")
    return new_wav


def downsample_from_csv(source: Path, dest: Path, dest_dir: Path):
    # check existence of the files
    if not source.exists():
        print(source.name + " not found")
        exit()
    if dest.exists():
        # conditionally remove old downsample csv
        print("Target: " + dest.name + " already exists, do you wish to remove it?")
        if input("y/n: ") == "y":
            os.remove(dest)
        else:
            print("Cancelling")
            exit()
    csv_dest = open(dest, "x", newline="")
    csv_writer = csv.writer(csv_dest, delimiter=",")
    # get total length of csv
    with open(source) as f:
        reader = csv.reader(f, delimiter=",")
        row_count = sum(1 for row in reader) - 1
    row_num = 1  # track progress
    # iterate through csv
    with open(source) as c:
        csv_reader = csv.reader(c, delimiter=",")
        # write header of old csv to new
        csv_writer.writerow(next(csv_reader))
        for line in csv_reader:
            # generate new audio
            audio_file_name = line[3]
            audio_file_parent = line[4]
            # create new directory structure
            new_parent = dest_dir / os.path.relpath(line[4])  # makes path relative to this location

            # check if that path is relative to current dir

            # if parent directory does not exist, create it and all other missing dirs in that path
            if not new_parent.exists():
                new_parent.mkdir(parents=True)

            new_audio_wav = deepspeech_resample(Path(audio_file_parent)/audio_file_name, new_parent)
            if not new_audio_wav:
                # downsample failed, go to next
                print("Resample failed")
                continue

            # get audio properties of new wav and ensure they match deepspeech requirements
            with wave.open(str(new_audio_wav), "rb") as wav:
                sample_rate = wav.getframerate()
                precision = wav.getsampwidth() * 8
                channels = wav.getnchannels()
            if not (sample_rate == 16000 and precision == 16 and channels == 1):
                print("Resulting file wrong")
                print(str(sample_rate) + ", " + str(precision) + ", " + str(channels))
                continue

            # write to dictionary
            data_dict = {
                "database": line[0],
                "source": line[1],
                "format": line[2],
                "audio_file_name": new_audio_wav.name,
                "audio_path": new_audio_wav.parent,
                "transcript": line[5],
                "aligned": line[6],
                "sampling": sample_rate,
                "recording_device": line[8],
                "bitrate": sample_rate * precision,
                "channels": channels,
                "precision": precision,
                "encoding": line[12],
                "date": line[13],
                "age": line[14],
                "gender": line[15],
                "accent": line[16],
                "country": line[17],
                "region": line[18],
                "user_name": line[19]
            }

            # write to csv
            csv_writer.writerow(data_dict.values())
            print("Resample completed: " + new_audio_wav.name + " (" + str(row_num) + " / " + str(row_count) + ")")
            row_num += 1

# set csv file to read and write to, and dir to place new audio in
# these should be customised based on the dataset being used
audio_csv = Path("output.csv")
dest_csv = Path("16kHz_output.csv")
target_dir = Path("16kHz_audio")

downsample_from_csv(audio_csv, dest_csv, target_dir)

#deepspeech_resample(Path("32242.mp3"), Path("new_audio"))
