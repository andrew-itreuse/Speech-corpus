# for each line in a given csv, check if it matches a given gender and accent string
from pathlib import Path
import csv
import shutil
import os

# files to create:
# deepspeech_csv.csv: in format expected by deepspeech
# search_terms.txt: text file showing the search strings
# all the audio files then go in a directory


def search_csv(file_list, gender: str, accent: str, dest: Path, copy_files: bool):
    # re-write to use a list of files
    if not dest.is_dir():  # create destination directory
        Path.mkdir(dest)
    # create text file containing search strings, as well as number of results to be added later
    with open(dest / "search_info.txt", "w") as lf:
        lf.write("Datasets searched: ")
        for i in file_list:
            lf.write(i[0] + ", ")
        lf.write("\n")
        lf.write("Accent: \"" + accent + "\"\n")
        lf.write("Gender: \"" + gender + "\"\n")

    # create deepspeech csv
    new_csv = dest / "search_res.csv"
    if new_csv.exists():
        os.remove(new_csv)

    # create directory for audio files
    audio_dir = dest / "audio"
    if not audio_dir.is_dir():
        Path.mkdir(audio_dir)
    else:
        return "Audio directory exists, this may cause errors\nProgram terminated"
    result_num = 0
    total_audio_size = 0
    total_audio_length = 0
    fail_num = 0
    sets_searched = len(file_list)
    set_num = 0
    for el in file_list:
        set_num += 1
        count = 0  # track result_num for this dataset
        if not el[1]:
            continue
        file = Path(el[1])
        working_dir = file.parent
        with file.open() as f:
            csv_reader = csv.reader(f, delimiter=",")
            next(csv_reader)  # skip header
            result_list = []
            for line in csv_reader:
                # get a list of all pertinent lines, and use to calculate total number to be converted
                line_gender = line[15]
                line_accent = line[16]

                # todo: calculate total size and length here, state it , state destination and ask for confirmation
                # test gender against search string
                if line_gender == gender or gender == "":
                    search_accent_length = len(accent)

                    # test accent against search string
                    if line_accent[:search_accent_length] == accent:
                        result_list.append(line)

        tot_lines = len(result_list)
        try:
            for line in result_list:

                result_num += 1
                count += 1
                # match found, get path to audio file
                audio_path = Path(working_dir / line[4]) / line[3]
                # in the new location, all files will be sat in one directory unless otherwise specified
                # no need to preserve the original path structure
                # each file needs a unique name: temporary measure: name file as result_num
                if copy_files:  # only copy if told to
                    shutil.copy(audio_path, audio_dir / (str(result_num) + ".wav"))

                # get size and add to total
                size = os.path.getsize(working_dir / line[4] / line[3])
                total_audio_size += size
                # get duration and add to total
                audio_duration = size / 32000
                total_audio_length += audio_duration
                # add line to csv
                wav_file_name = str(result_num) + ".wav"
                wav_file_size = size
                transcript = line[5]
                with new_csv.open("a", newline="") as c:
                    csv_writer = csv.writer(c, delimiter=",")
                    csv_writer.writerow([wav_file_name, wav_file_size, transcript])
                # print progress
                if result_num % 64 == 0:  # only print one in 64
                    print(str(count) + " / " + str(tot_lines) + " (set " + str(set_num) + " / " + str(sets_searched) + ")")
        except:
            fail_num += 1
    # write search result metadata
    with open(dest / "search_info.txt", "a") as lf:
        lf.write("Original directory: " + os.getcwd() + "\n")
        lf.write("Number of audio files: " + str(result_num) + "\n")
        lf.write("Size of audio files: " + str(total_audio_size) + " B ("
                 + str(total_audio_size / (1024*1024)) + " MB)\n")
        # convert duration to human readable format
        h = int(total_audio_length // 3600)
        m = str(int((total_audio_length % 3600) // 60))
        if len(m) < 2:
            m = "0" + m
        s = str(int(total_audio_length % 60))
        if len(s) < 2:
            s = "0" + s
        lf.write("Approx length of audio files: " + str(total_audio_length)
                 + "s (" + str(h) + ":" + m + ":" + s + ")\n")
    return fail_num


# set directory for csv, to allow proper retrieval of audio files

# paths to the different csv files
# given as a list [dataset name, absolute path to csv]
mcgill = ["McGill-TSP", "/mnt/big-drive-2001-gp3/data/McGill-TSP/McGill_restructured.csv"]
nigerian = ["NigerianEnglish", "/mnt/big-drive-2001-gp3/data/NigerianEnglish/16kHz_restructured.csv"]
simplevoice = ["SimpleVoice", "/mnt/big-drive-2001-gp3/data/SimpleVoice/16kHz_output.csv"]  # not yet done
tatoeba = ["Tatoeba", "/mnt/big-drive-2001-gp3/data/Tateoba/Tatoeba_restructured.csv"]
ukaccents = ["UKAccents", "/mnt/big-drive-2001-gp3/data/UKAccents/UKAccents_restructured.csv"]
vctk = ["VCTK-Corpus-0.92", "/mnt/big-drive-2001-gp3/data/VCTK-Corpus-0.92/VCTK_restructured.csv"]
voxforge = ["voxforge-org", "/mnt/big-drive-2001-gp3/data/voxforge-org/voxforge_16kHz_restructured.csv"]
libriAdapt_respeaker = ["LibriAdapt respeaker", "/mnt/big-drive-2001-gp3/data/LibriAdapt/respeaker_restructured.csv"]
libriAdapt_usb = ["LibirAdapt usb", "/mnt/big-drive-2001-gp3/data/LibriAdapt/usb_restructured.csv"]

all_data = [mcgill, nigerian, simplevoice, tatoeba, ukaccents, vctk, voxforge]  # all bar libriadapt: data is not good


#target_files = [simplevoice]  # give a list of files
#search_gender = "female"  # gender search string
#search_accent = "UK"  # accent search string
#copy_audio = False  # do you want to copy the audio, or just get search info
#new_dir = Path("new_audio_directory1")  # path for results to be saved
#res = search_csv(target_files, search_gender, search_accent, new_dir, copy_audio)
#print(res)  #  number of failed files