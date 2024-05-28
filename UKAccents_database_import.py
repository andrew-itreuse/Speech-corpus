from pathlib import Path
import csv
import wave
import os
import re

# declare initial variables
transcriptFile = "line_index.csv"  # each transcript has the same name
# csv file for destination, is created for this but ultimately will be a noSQL database
# check if exists, and if so destroy
p = Path("output.csv")
if p.exists():
    os.remove(p)
dataDest = open(p, "x", newline="")
csvWriter = csv.writer(dataDest, delimiter=",")
# write headers to file (just temp placeholder)
csvWriter.writerow(["database", "source", "format", "audioFileName", "audioPath", "transcript",
                    "aligned", "sampling", "recording device", "bitrate", "channels", "precision", "encoding", "date",
                    "age", "gender", "accent", "country", "region", "user_name"])


# remove special characters from transcript
def parse_transcript(text):
    text = re.sub("[^a-z ]+", "", text.lower()).strip()
    return text


# general function for each one, parameters are (folder, gender, accent, country, region)
def import_data(folder, speaker_gender, speaker_accent, speaker_country, speaker_region):
    dataPath = Path(folder)
    i = 0
    # open csv
    with open(dataPath / transcriptFile) as transcript:
        csvReader = csv.reader(transcript, delimiter=",")
        for row in csvReader:
            # read each row
            # from csv
            # get details from wav file
            audioPath = dataPath / (row[1].strip() + ".wav")
            with wave.open(str(audioPath), "rb") as wav:
                wav_sampleRate = wav.getframerate()
                wav_precision = wav.getsampwidth() * 8
                wav_channels = wav.getnchannels()
                wav.close()

            # set variable for each entry in data csv
            database = "UK Accents"
            source = "UK_Accents"
            format = "wav"
            audioFileName = row[1].strip() + ".wav"
            audioPath = dataPath
            transcript = parse_transcript(row[2].strip())
            aligned = True
            sampling = wav_sampleRate
            rec_dev = "Rode M5 microphone, Blue Icicle XLR-USB A/D converter"
            bitrate = wav_sampleRate * wav_precision * wav_channels
            channels = wav_channels
            precision = wav_precision
            encoding = "PCM"
            date = "unknown"
            age = "unknown"
            gender = speaker_gender
            accent = speaker_accent
            country = speaker_country
            region = speaker_region
            user_name = "unknown"

            # write this lot to csv
            csvWriter.writerow([database, source,format, audioFileName, audioPath, transcript,
                               aligned, sampling, rec_dev, bitrate, channels, precision, encoding, date,
                               age, gender, accent, country, region, user_name])


# import for all folders
import_data("irish_english_male", "male", "Irish", "Ireland", "Ireland")
print("irish")
import_data("midlands_english_female", "female", "English", "England", "Midlands")
import_data("midlands_english_male", "male", "English", "England", "Midlands")
print("midlands")
import_data("northern_english_female", "female", "English", "England", "Northern")
import_data("northern_english_male", "male", "English", "England", "Northern")
print("north")
import_data("scottish_english_female", "female", "Scottish", "Scotland", "Scotland")
import_data("scottish_english_male", "male", "Scottish", "Scotland", "Scotland")
print("scotland")
import_data("southern_english_female", "female", "English", "England", "Southern")
import_data("southern_english_male", "male", "English", "England", "Southern")
print("south")
import_data("welsh_english_female", "female", "Welsh", "Wales", "Wales")
import_data("welsh_english_male", "male", "Welsh", "Wales", "Wales")

# still need to filter to just allowed regex
print("done")
