import csv
from pathlib import Path
import os
import re
import sox
import pyogg

root_dir = os.getcwd()  # directory of python file, to allow easy switching back when changed
# check if csv exists, if so destroy
if Path("output.csv").is_file():
    Path("output.csv").unlink()
# create csv
dataDest = open("output.csv", "x", newline="")
csvWriter = csv.writer(dataDest, delimiter=",")
# write headers to file (just temp placeholder)
csvWriter.writerow(["database", "source", "format", "audioFileName", "audioPath", "transcript",
                    "aligned", "sampling", "recording device", "bitrate", "channels", "precision", "encoding", "date",
                    "age", "gender", "accent", "country", "region", "user_name"])

def get_user_genders():  # generate dictionary of user ID and gender, as M/F
    with open("metainfo.txt", newline="", encoding="utf8") as users:
        reader = csv.reader(users, delimiter="|")
        next(reader, None)  # skip header
        info_dict = {}
        try:
            for row in reader:
                # each will be a list
                info_dict.update({row[0].strip(): row[1].strip()})
        except Exception as e:
            print(e)
    return info_dict


def transcript_regex_filter(transcript):  # general function to take a transcript snippet and make it match the regex [a-z ]+ per deepspeech requirements
    text = re.sub("[^a-z ]+", "", transcript)
    return text


def get_audio_info(file_name):
    # need sample frequency, bitrate, channels, precision, encoding
    # TODO: modify this for wav file once converted
    audio_details = {
        "frequency": pyogg.OpusFile(file_name).frequency,
        "bitrate": "Unknown",
        "channels": pyogg.OpusFile(file_name).channels,
        "precision": "Unknown",
        "encoding": "Unknown"
    }
    return audio_details


def export_dir(dir_name, users):  # export contents of dir to database

    p = Path(dir_name)
    with open(p / "transcripts.txt", newline="", encoding="utf8") as transcripts:
        reader = csv.reader(transcripts, delimiter="\t")
        for row in reader:
            row[1] = transcript_regex_filter(row[1])
            # get audio file details
            try:  # for test not all files there, ignore any missing audio files
                audio_path = row[0].split("_")
                audio_file_dir = p / "audio" / audio_path[0] / audio_path[1]
                audio_file_name = row[0] + ".opus"
                audio_file = audio_file_dir / audio_file_name
                audio_file_transcript = row[1]
                user_name = str(audio_path[0])

                # get audio file properties
                os.chdir(audio_file_dir)
                audio_info = get_audio_info(audio_file_name)
                # return to previous working directory
                global root_dir
                os.chdir(root_dir)
            except:
                continue

            # generate database entry
            data_dict = {
                "database": "MLSLibrispeech",
                "source": "MLSLibrispeech",
                "format": "opus",
                "audio_file_name": audio_file_name,
                "audio_path": audio_file_dir.as_posix(),
                "transcript": audio_file_transcript,
                "aligned": "True",
                "sampling": audio_info["frequency"],
                "recording_device": None,
                "bitrate": audio_info["bitrate"],
                "channels": audio_info["channels"],
                "precision": audio_info["precision"],
                "encoding": audio_info["encoding"],
                "date": None,
                "age": None,
                "gender": users[user_name],
                "accent": None,
                "country": None,
                "region": None,
                "user_name": user_name
            }
            # write to csv
            csvWriter.writerow(list(data_dict.values()))
user_dict = get_user_genders()
# with pathlib, open folders in turn
# ignore train for now, far too big and has the same structure as the other two
# then open transcripts.txt
# iterate through each line to get path from first value and transcript from second

export_dir("dev", user_dict)
export_dir("test", user_dict)
# export_dir("train")

