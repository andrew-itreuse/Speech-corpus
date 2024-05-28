from resampler import deepspeech_resample  # call functions from the resampler
import csv
from pathlib import Path
import re
import wave
import os


# create csv output file
p = Path("output.csv")
if p.exists():
    os.remove(p)
csv_writer = csv.writer(open("output.csv", "x", newline=""))
csv_writer.writerow(["database", "source", "format", "audio_file_name", "audio_path", "transcript",
                     "aligned", "sampling", "recording device", "bitrate", "channels", "precision", "encoding", "date",
                     "age", "gender", "accent", "country", "region", "user_name"])

# create new audio dir: wav16
# this will contain the audio in wav files resampled 20 16KHz
# audio_file = Path("wav48_silence_trimmed\\p225\\p225_004_mic1.flac")
dest_dir = Path("wav16")
source_dir = Path("wav48_silence_trimmed")
speaker_info = Path("speaker-info.txt")
transcript_dir = Path("txt")

if not dest_dir.is_dir():
    dest_dir.mkdir()


def transcript_regex_filter(transcript):  # take a transcript snippet and make it match the regex [a-z ]+
    text = re.sub("[^a-z ]+", "", transcript.lower())
    return text


# count failed audio files and lsit as such
i = 0
failed_audio = []
missing_dirs = []


def iterate_users(info, source, txt, dest):
    global i
    global missing_dirs
    # track progress
    j = 0
    with open(info, encoding="utf8") as f:
        f.readline()  # skip first line
        for line in f:
            # modify line to remove commentary and additional whitespace
            line = re.sub("\\(.*\\)", "", line)
            line = re.sub(" +", " ", line).strip()
            list_line = line.split(" ", 4)  # some lack region, some regions have spaces
            user_id = list_line[0]
            age = list_line[1]
            gender = list_line[2]
            accent = list_line[3]
            # some regions missing, set as unknown
            try:
                region = list_line[4]
            except:
                region = "Unknown"
            # check existence of audio directory and user directory
            if not ((source / user_id).is_dir() and (txt / user_id).is_dir()):
                print("missing directory: " + user_id)
                missing_dirs.append(user_id)
                continue

            # open user transcript dir and iterate through transcripts files
            user_dest = dest / user_id
            if not user_dest.exists():
                user_dest.mkdir()

            for transcript in (txt / user_id).iterdir():
                flac = source / user_id / (transcript.stem + "_mic1.flac")
                # convert flac to wav, down sample and place in dest
                wav = deepspeech_resample(flac, user_dest)
                if not wav:  # resample failed for some reason
                    print("Resample failed")
                    failed_audio.append(user_id + "/" + transcript.stem)
                    i += 1
                    continue
                # get data from transcript file
                with open(transcript, encoding="utf8") as t:
                    # remove whitespace and special characters
                    line = transcript_regex_filter(t.readline().strip())
                # get audio properties of wav file
                with wave.open(str(wav), "rb") as wav_file:
                    wav_sampleRate = wav_file.getframerate()
                    wav_precision = wav_file.getsampwidth() * 8
                    wav_channels = wav_file.getnchannels()
                if not (wav_sampleRate == 16000 and wav_precision == 16 and wav_channels == 1):
                    print("Error in wav file of :" + wav.name)
                    print(wav_channels)
                    print(wav_precision)
                    print(wav_sampleRate)
                    failed_audio.append(user_id + "/" + transcript.stem)
                    i += 1
                    continue
                # generate entry for that audio
                data_dict = {
                    "database": "VCTK",
                    "source": "VCTK-Corpus-0.92",
                    "format": "wav",
                    "audio_file_name": wav.name,
                    "audio_path": wav.parent,
                    "transcript": line,
                    "aligned": True,
                    "sampling": wav_sampleRate,
                    "recording_device": "DPA 4035 omni-directional microphone",
                    "bitrate": wav_sampleRate * wav_precision,
                    "channels": wav_channels,
                    "precision": wav_precision,
                    "encoding": "16-bit PCM",
                    "date": "Unknown",
                    "age": age,
                    "gender": gender,
                    "accent": accent,
                    "country": accent,  # actual country not stated, but accent should be the same
                    "region": region,
                    "user_name": user_id
                }
                # write to csv
                csv_writer.writerow(data_dict.values())
                print(wav.stem + " resampled and saved")
                print(str(j) + " / 109 completed")

            j += 1
            print(str(j) + " / 109 completed")

iterate_users(speaker_info, source_dir, transcript_dir, dest_dir)
# report any failed audio files or directories
print(str(i) + " audio file failed to convert")
print(failed_audio)
if len(missing_dirs) > 0:
    print("The following users are missing one or both directories: ")
    print(missing_dirs)
