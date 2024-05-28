from pathlib import Path
from sox import Transformer
# import shutil
import re
import wave
import os
import csv
# import tedlium data to database
# creates set of partitioned audio files in partitioned_audio directory
# creates csv of each audio file in that directory


# set directory for partitioned audio to go
target_dir = Path("partitioned_audio")

# create csv output file
p = Path("output.csv")
if p.exists():
    os.remove(p)
csv_writer = csv.writer(open("output.csv", "x", newline=""))
csv_writer.writerow(["database", "source", "format", "audio_file_name", "audio_path", "transcript",
                     "aligned", "sampling", "recording device", "bitrate", "channels", "precision", "encoding", "date",
                     "age", "gender", "accent", "country", "region", "user_name"])


def reset_dir():  # create new directory to store the audio
    # within this directory will be a directory for each talk
    if Path.exists(target_dir):
        # shutil.rmtree(target_dir)  # this is overkill, only to be used in testing
        print("Target directory still exists, pls fix")
        exit()
    Path.mkdir(target_dir)


def parse_transcript(text):  # adjust transcript to be suitable for deepspeech
    # remove spaces before apostrophes, and apostrophes themselves
    text = text.replace(" '", "")
    # remove instances of <unk>
    text = text.replace("<unk>", "")
    # ensure compliance with required regex and remove leading/trailing whitespace
    text = re.sub("[^a-z ]+", "", text.lower()).strip()
    return text


def split_wav(origin, start, time, wav):
    framerate = origin.getframerate()  # number of samples per second
    start_frame = int(framerate * start)
    origin.setpos(int(start_frame))
    segment_data = origin.readframes(int((time - start) * framerate))  # get the relevant segment
    # create new wav file and write the segment, along with relevant parameters
    segment_audio = wave.open(wav, "w")
    segment_audio.setnchannels(origin.getnchannels())
    segment_audio.setsampwidth(origin.getsampwidth())
    segment_audio.setframerate(framerate)
    segment_audio.writeframes(segment_data)
    segment_audio.close()
    return


def write_csv_element(user, text, audio_path, audio_data):
    # generate JSON
    data_dict = {
        "database": "Tedlium",
        "source": "TED",
        "format": "wav",
        "audio_file_name": audio_path.name,
        "audio_path": str(audio_path.parent),
        "transcript": text,
        "aligned": "True",
        "sampling": audio_data["sampling"],
        "recording_device": "Unknown",
        "bitrate": audio_data["bitrate"],
        "channels": audio_data["channels"],
        "precision": audio_data["precision"],
        "encoding": audio_data["encoding"],
        "date": "Unknown",
        "age": "Unknown",
        "gender": "Unknown",
        "accent": "Unknown",
        "country": "Unknown",
        "region": "Unknown",
        "user_name": user
    }
    # write JSON to csv
    csv_writer.writerow(data_dict.values())


# iterate through audio files and transcripts
data_dir = Path("TEDLIUM_release-3") / "data"
audio_dir = data_dir / "sph"
transcript_dir = data_dir / "stm"
# csv with transcripts and such will be outside this dir

reset_dir()

failnum = 0  # number of failures due to incorrect audio details, e.g wrong bitrate
j = 0  # count talk number, to track speed
for sph in audio_dir.iterdir():
    j = j + 1
    # temp for testing, only use al gore 2006
    if not sph.suffix == ".sph":
        continue
    # get relevant transcript file
    transcript_file = transcript_dir / (sph.stem + ".stm")
    wav_dir = target_dir / sph.stem
    Path.mkdir(wav_dir)
    # transform sph to wav and put wav in new location
    transformer = Transformer()
    wav_filename = sph.stem + ".wav"
    wav_file = wav_dir / wav_filename
    transformer.build(str(sph), str(wav_file))
    # open wav for use by splitter
    audio = wave.open(str(wav_file), "r")
    # get and check audio file properties
    audio_properties = {
        "sampling": audio.getframerate(),
        "bitrate":  audio.getframerate() * audio.getsampwidth() * 8,  # sampwidth is in bytes
        "channels": audio.getnchannels(),
        "precision": audio.getsampwidth() * 8,
        "encoding": "LPCM"
    }
    if not(audio_properties["sampling"] == 16000 and audio_properties["bitrate"] == 256000 and
           audio_properties["channels"] == 1 and audio_properties["precision"] == 16):
        print("audio not correct type: " + sph.name)
        failnum += 1
    # parse transcript to get data
    # should be done line by line to also perform the splits
    with open(transcript_file) as f:
        # count each line for audio file name
        i = 0
        for line in f:
            i += 1
            # split into list
            line = line.split(" ", 6)
            user_name = line[0]
            channels = line[1]
            speaker_id = line[2].split("_")[0]  # username is part before _, year is after
            start_time = float(line[3])
            end_time = float(line[4])
            tags = line[5]  # useless, discard
            transcript = parse_transcript(line[6])
            new_wav_file = wav_dir / (wav_file.stem + "_" + str(i) + ".wav")
            split_wav(audio, start_time, end_time, str(new_wav_file))
            write_csv_element(speaker_id, transcript, new_wav_file, audio_properties)
    print(str(j) + " / 2351 done")
print(str(failnum) + " audio files do not conform to DeepSpeech requirements")
