from pathlib import Path
import re
import csv
import os

# create csv output file
p = Path("output.csv")
if p.exists():
    os.remove(p)
csv_writer = csv.writer(open("output.csv", "x", newline=""))
csv_writer.writerow(["database", "source", "format", "audio_file_name", "audio_path", "transcript",
                     "aligned", "sampling", "recording device", "bitrate", "channels", "precision", "encoding", "date",
                     "age", "gender", "accent", "country", "region", "user_name"])

# parameters for reading bytes, for convenience
little_endian = "little"
u = "utf-8"


def transcript_regex_filter(transcript):  # take a transcript snippet and make it match the regex [a-z ]+
    text = re.sub("[^a-z ]+", "", transcript.lower())
    return text


def parse_riff(file_name):  # parse the entire file header
    with open(file_name, "rb") as f:
        riff = (f.read(4).decode(u) == "RIFF")  # get section marking as riff
        if not riff:
            return "not RIFF"
        file_size = int.from_bytes(f.read(4), little_endian) + 8  # not relevant but might as well have it
        wav = (f.read(4).decode(u) == "WAVE")
        if not wav:
            return "not WAV"
        fmt = f.read(4).decode(u).strip()
        fmt_length = int.from_bytes(f.read(4), little_endian)
        if fmt != "fmt":
            return "not fmt"
        fmt_contents = f.read(fmt_length)
        fmt_data = parse_fmt(fmt_contents)

        # read list data
        list_head = f.read(4).decode(u)
        if list_head != "LIST":
            return "not list"
        list_length = int.from_bytes(f.read(4), little_endian)
        list_type = f.read(4).decode(u)
        list_contents = f.read(list_length - 4)  # actual data in list
        list_dict = parse_list(list_contents, {})  # get list data as a dictionary
        # check for and parse afsp chunk
        afsp_chunk_head = f.read(4).decode(u)
        if not afsp_chunk_head.upper() == "AFSP":
            return "afsp chunk not found where expected"
        # pad afsp chunk length to be even
        afsp_length = int.from_bytes(f.read(4), little_endian)
        if afsp_length % 2 == 1:
            afsp_length += 1
        afsp_data = parse_afsp(f.read(afsp_length))  # extract data from afsp section of header

        # check for next chunk to ensure it is data
        data_chunk_head = f.read(4).decode(u)
        # slight weird issue with a single byte not included in any chunk
        # probably caused by chunks needing to start at even positions, and afsp has an odd length
        # to test, check afsp length and if odd add 1
        # seems to work, but need to keep an eye out for problems
        if not data_chunk_head.upper() == "DATA":
            return "somethings wrong"
        # we now have all header data, format to expected json
        # print(fmt_data)
        # print(list_dict)
        # print(afsp_data)
    # some additional processing on data needed to get gender and age
    data_dict = {
        "database": "McGill TSP",
        "source": "McGill-TSP",
        "format": "wav",
        "audio_file_name": file_name.name,
        "audio_path": str(file_name.parent),
        "transcript": transcript_regex_filter(afsp_data["text"]),
        "aligned": "True",
        "sampling": fmt_data["sample_rate"],
        "recording_device": afsp_data["recording_conditions"],
        "bitrate": fmt_data["byterate"] * 8,
        "channels": fmt_data["channels"],
        "precision": fmt_data["bit_depth"],
        "encoding": "fmt",
        "date": list_dict["ICRD"][:10],
        "age": list_dict["INAM"],  # is extracted later
        "gender": list_dict["INAM"].split(" ")[0],  # gender is first word here
        "accent": None,  # 24 speakers, mostly canadian english, manual accent classification possible
        "country": "Canada",
        "region": None,
        "user_name": afsp_data["speaker"]
    }
    return data_dict


def parse_list(info, list_dict):  # this seems to work well enough
    # will take as args the remaining contents in the list and a dict to put them in
    # will return dict of all list elements
    if len(info) == 0:
        return list_dict
    # need to check for leading 0 and remove if necessary
    while info[0] == 0:
        info = info[1:]
    info_id = info[:4].decode(u)  # separate first tag
    info = info[4:]
    info_len = int.from_bytes(info[:4], little_endian)  # get length of first entry
    info = info[4:]
    info_data = info[:info_len].decode(u).strip("\x00")
    list_dict.update({info_id: info_data})  # record element
    info = info[info_len:]  # trim bytes
    list_dict = parse_list(info, list_dict)  # if more entries, they add on new elements
    return list_dict  # return the full list


def parse_fmt(chunk):  # parse fmt chunk and return data, works well
    # bytes type is a list of bytes, list is split into the sections specified for fmt
    chunk_info = {
        "audio_format": int.from_bytes(chunk[0:2], little_endian),  # value of 1 is pcm, otherwise who knows
        "channels": int.from_bytes(chunk[2:4], little_endian),  # number of channels of audio
        "sample_rate": int.from_bytes(chunk[4:8], little_endian),  # sample rate of audio file
        "byterate": int.from_bytes(chunk[8:12], little_endian),  # bytes per second of audio
        "block_align": int.from_bytes(chunk[12:14], little_endian),  # bytes per sample across all channels, expect 2
        "bit_depth": int.from_bytes(chunk[14:16], little_endian)  # bits per sample, expect 16
    }
    return chunk_info


def parse_afsp(chunk):  # working!!!!!!
    data = {}
    # extract data from afsp to list
    chunk_str = chunk.decode(u).replace("\n", " ").strip("\x00")
    chunk_list = chunk_str.split("\x00")
    # convert list to dict by splitting each element once with delimiter=": ",
    for entry in chunk_list:
        entry_as_list = entry.split(": ", 1)
        data.update({entry_as_list[0]: entry_as_list[1]})
    return data


# print(parse_riff("FK61_05.wav"))
# now iterate through all the speakers
# for dir in 16k-LP7:
#   for audio_file in dir:
#       file_data = parse_riff(audio_file)
#       save_file_data_to_csv

audio_dir = Path("16k-LP7")
for speaker in audio_dir.iterdir():# iterate through different speakers
    # ignore non directories
    if speaker.is_file():
        continue
    for audio_file in speaker.iterdir():  # iterate through files in each speaker directory
        # ignore non wav files
        if not audio_file.suffix == ".wav":
            continue

        audio_details = parse_riff(audio_file)
        # extract info from age, gender and accent
        # for age, look for text in brackets, if none then adult, else get number from it
        if "(" in audio_details["age"]:
            age = re.search(r"\((.*)\)", audio_details["age"])
            audio_details.update({"age": int(age.group(1)[4:])})
        else:  # is not child
            audio_details.update({"age": "adult"})
        # print(audio_details)
        # audio details now parsed, accent needs classifying and details need exporting to csv
        # classify accents based on user dir
        user = speaker.name
        if user in {"CA", "CB", "FA", "FC", "FD", "FE", "FE",
                    "FG", "FH", "FI", "FJ", "FK", "FL", "MA",
                    "MB", "MC", "MD", "MF", "MG", "MH", "MJ", "MK", "ML"}:  # users with canadian accents
            audio_details.update({"accent": "Canadian"})
        elif user == "FB":
            audio_details.update({"accent": "English"})
        elif user == "MI":
            audio_details.update({"accent": "Scottish"})

        # write results to csv
        csv_writer.writerow(audio_details.values())
