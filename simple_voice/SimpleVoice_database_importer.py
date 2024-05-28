from _csv import reader
from pathlib import Path
import csv
import wave
import os
import glob
import re
import eyed3

dataSource = "/mnt/big-drive-2001-gp3/data/SimpleVoice/"
os.chdir(dataSource)
p = Path("dev_output.csv")
# check if csv exists,if so destroy
if p.is_file():
    p.unlink()
dataDest = open("dev_output.csv", "x", newline="")
csvWriter = csv.writer(dataDest, delimiter=",")
csvWriter.writerow(["database", "source", "format", "audioFileName", "audioPath", "transcript", "aligned", "sampling",
                    "recording device", "bitrate", "channels", "precision", "encoding", "date", "age", "gender",
                    "accent", "country", "region", "user_name"])


def transcript_regex_filter(
        transcript):  # general function to take a transcript snippet and make it match the regex[a-z ]+ per deepspeech requirements
    text = re.sub("[^a-z ]+", "", transcript.lower())
    return text


def import_data(folder,tsv_transcript):
    dataPath = Path(dataSource+folder+"/"+tsv_transcript)
    with open(dataPath) as transcript:
        tsv_file = open(folder+"/"+tsv_transcript)
        read_tsv = csv.reader(transcript, delimiter="\t")
        #contents = transcript.readlines()
        next(read_tsv)  # skip header
        for row in read_tsv:
            # read each row from tsv
            # get details from wav file
            row[2] = transcript_regex_filter(row[2])
            audioPath_transcript = row[1]
            audioPath = dataSource + folder + "/clips/"
            audio_files = audioPath + '*.mp3'
            #audiofile = eyed3.load(audio_files
            data_dict = {"database": "SimpleVoice", "source": "SimpleVoice", "format": "mp3", "audioFileName": row[1].strip(), "audioPath": audioPath, "transcript": row[2].strip(),"aligned": True, "sampling": "48000 Hz", "recording_device": "unknown","bitrate": "unknown", "channels": "unknown", "precision": "unknown","encoding": "none", "date": "unknown", "age": row[5].strip(), "gender": row[6].strip(), "accent": row[7].strip(), "country": row[7].strip(), "region": row[7].strip(), "user_name": row[0].strip()}
            csvWriter.writerow(list(data_dict.values()))
        tsv_file.close()


#import_data("cv-corpus-5.1-2020-06-22/en","validated.tsv");
import_data("cv-corpus-5.1-2020-06-22/en","dev.tsv")
#import_data("cv-corpus-5-singleword/en","validated.tsv");
