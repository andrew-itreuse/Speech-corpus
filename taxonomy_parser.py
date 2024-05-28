# convert accent data to standardised form
# TODO: convert entire csv
# TODO: apply the same function to gender
import json
import csv
import re
# start by importing the accent part of the JSON as a list
with open("taxonomy.json") as json_file:
    taxonomy = json.load(json_file)
    accent_data = taxonomy["accent"]
    gender_data = taxonomy["gender"]


# generate taxonomy for accent, region and country
def gen_accent_category(accent, country, region):
    # check accent, region and country separately, if different log
    # can be used to find accent, region and country taxonomy
    # can also be used to check an output.csv for any countries, accents and regions not present
    accent_tax = ""
    country_tax = ""
    region_tax = ""
    accent_found = False
    country_found = False
    region_found = False
    # remove unknown values, but still pass through taxonomy unknown
    if accent.lower() == "unknown":
        accent_found = True
        accent_tax = ["Unknown"]

    if country.lower() == "unknown":
        country_found = True
        country_tax = ["Unknown"]

    if region.lower() == "unknown":
        region_found = True
        region_tax = ["Unknown"]
    for section in accent_data:
        # for accent, region and country, search for matching string
        # once string has been found, stop search
        if not accent_found:
            # this will only get the first result, ignoring duplicates
            # duplicates can be tested for and resolved by some other process, that would add a lot of overhead
            result = region_membership(section, accent)
            if result:
                accent_found = True
                accent_tax = result

        if not country_found:
            result = region_membership(section, country)
            if result:
                country_found = True
                country_tax = result

        if not region_found:
            result = region_membership(section, region)
            if result:
                region_found = True
                region_tax = result

    # handle any accents or countries not found, then return since that data can't be used
    invalid_string = False  # are any of the three missing?
    if not accent_found:
        invalid_string = True
        print("accent not found: " + accent)
    if not country_found:
        invalid_string = True
        print("country not found: " + country)
    if not region_found:
        invalid_string = True
        print("region not found: " + region)
    if invalid_string:
        return False

    return [accent_tax, country_tax, region_tax]


# search a region selection for a given string, depth first (should probably be breadth first, but this was easier)
def region_membership(region_entry, region):
    # if correct region has been found, return it
    if region in region_entry[1]:
        return [region_entry[0]]
    else:
        # otherwise, check for region in each subregion
        for sub in region_entry[2]:
            entry = region_membership(sub, region)
            # if found, add this layer to the list and return it
            if entry:
                entry.append(region_entry[0])
                return entry
    return False  # if region is not found anywhere, move on


# check a standard output.csv file for any new country strings
def get_new_country_strings(file: str):
    with open(file) as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader, None)  # skip header
        i = 1  # track line number for errors
        not_found_set = set()
        for line in csv_reader:
            i = i + 1
            accent = line[16]
            country = line[17]
            region = line[18]
            result = gen_accent_string(accent, country, region)
            if result:
                continue

            else:
                not_found_set.add(accent + ", " + country + ", " + region)
                print("Error at line: " + str(i))
        print("set of accents not found in taxonomy:")
        print(not_found_set)


def parse_transcript(text):
    text = re.sub("[^a-z ]+", "", text.lower()).strip()
    return text


# generate a string for the accent taxonomy in the form a>b>c
def gen_accent_string(accent, country, region):
    # get each separately
    accents = gen_accent_category(accent, country, region)

    # replace unknown with empty string, means it will always match and will be discarded first
    if not accents:
        print("not accents")
        return False
    for i in range(len(accents)):
        try:
            if accents[i][0] == "Unknown":
                accents[i] = ""
        except Exception as e:
            print(i)
            print(e)
            print(accents)
            quit()

    # some will have all values unknown
    # need to return "Unknown"
    if accents[0] == "" and accents[1] == "" and accents[2] == "":
        return "Unknown"
    accent_l = accents[0]
    country_l = accents[1]
    region_l = accents[2]

    # first convert to string
    # then check equivalence of characters in string
    accent_str = ""

    for word in accent_l:
        accent_str = word + ">" + accent_str
    accent_str = accent_str[:-1]  # remove last >

    country_str = ""
    for word in country_l:
        country_str = word + ">" + country_str
    country_str = country_str[:-1]  # remove last >
    region_str = ""
    for word in region_l:
        region_str = word + ">" + region_str
    region_str = region_str[:-1]  # remove last >
    # get length of shortest, compare etc
    shortest_len = min(len(accent_str), len(country_str), len(region_str))
    if region_str[:shortest_len] == accent_str[:shortest_len] == country_str[:shortest_len]:
        # we're good, remove shortest
        longest = []
        # put any longer than shortest string in new array
        if len(region_str) > shortest_len:
            longest.append(region_str)
        if len(accent_str) > shortest_len:
            longest.append(accent_str)
        if len(country_str) > shortest_len:
            longest.append(country_str)

        if len(longest) == 0:
            # all are the same length, send through accent_str
            print(accent_str)
            return accent_str
        elif len(longest) == 1:
            # only 1 left and all match, send it through
            return longest[0]
        elif len(longest) > 2:
            # not sure how this could happen, but best to be safe
            print("You done goofed")
        else:
            # compare and see what's up
            min_len = min(len(longest[0]), len(longest[1]))
            if longest[0][:min_len] == longest[1][:min_len]:
                # return the longest string
                if len(longest[0]) > len(longest[1]):
                    return longest[0]
                else:
                    return longest[1]
            else:
                # error, say what's up
                print("error: non matching strings")
                print(longest[0])
                print(longest[1])
                return False

    else:
        # vctk specific issues
        # caused by my inept parsing of vctk, but fixed by hacky code
        vctk = True
        if vctk:
            if region == "Perth" and accent == "Scottish" and country == "Scottish":
                return "UK>Scotland>Perth"
            if region == "English" and accent == "NewZealand" and country == "NewZealand":
                return "NZ"
            if region == "English" and accent == "Australian" and country == "Australian":
                return "Australia"
        print("error: non matching strings:")
        #print(region_str)
        print("region: " + region)
        #print(accent_str)
        print("accent: " + accent)
        #print(country_str)
        print("country: " + country)
        return False


def get_new_gender_strings(file: str):
    with open(file) as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader, None)  # skip header
        i = 1  # track line number
        not_found_genders = set()
        for line in csv_reader:
            i += 1
            gender = line[15]
            if gender in gender_data[0][1]:
                gender_str = gender_data[0][0]
            elif gender in gender_data[1][1]:
                gender_str = gender_data[1][0]
            elif gender in gender_data[2][1]:
                gender_str = gender_data[2][0]
            else:
                not_found_genders.add(gender)
    print(not_found_genders)


def gen_gender_str(gender):
    if gender in gender_data[0][1]:
        gender_str = gender_data[0][0]
    elif gender in gender_data[1][1]:
        gender_str = gender_data[1][0]
    elif gender in gender_data[2][1]:
        gender_str = gender_data[2][0]
    else:
        gender_str = False
    return gender_str


def restructure_csv(file: str, dest: str):
    with open(dest, "w", newline="") as d:
        csv_writer = csv.writer(d, delimiter=",")
        csv_writer.writerow(["database", "source", "format", "audio_file_name", "audio_path",
                             "transcript", "aligned", "sampling", "recording_device",
                             "bitrate", "channels", "precision", "encoding",
                             "date", "age", "gender", "accent", "user_name"])
    with open(file) as f:
        csvreader = csv.reader(f, delimiter=",")
        next(csvreader, None)  # skip header
        line_fail_num = 0  # track number of lines that fail for some reason
        for line in csvreader:
            # read line, convert to new json

            accent = line[16]
            country = line[17]
            region = line[18]
            accent_str = gen_accent_string(accent, country, region)
            if not accent_str:
                # accent string non matching
                line_fail_num += 1
                # could log lines that failed, but honestly not worth it
                # if more than 1% fail, then maybe
                print("FAIL accent: " + accent + "," + country + "," + region)
                continue
            gender = line[15]
            gender_str = gen_gender_str(gender)
            if not gender_str:
                # non-matching string
                line_fail_num += 1
                print("FAIL gender: " + gender)
                continue

            new_data_dict = {
                "database": line[0],
                "source": line[1],
                "format": line[2],
                "audio_file_name": line[3],
                "audio_path": line[4],
                "transcript": parse_transcript(line[5]),  # just in case
                "aligned": line[6],
                "sampling": line[7],
                "recording_device": line[8],
                "bitrate": line[9],
                "channels": line[10],
                "precision": line[11],
                "encoding": line[12],
                "date": line[13],
                "age": line[14],
                #"gender": line[15],
                "gender": gender_str,
                #"accent": line[16],
                #"country": line[17],
                #"region": line[18],
                "accent": accent_str,
                "user_name": line[19]
            }
            # write to csv
            with open(dest, "a", newline="") as d:
                csv_writer = csv.writer(d, delimiter=",")
                csv_writer.writerow(new_data_dict.values())
        print(line_fail_num)
# generate the arrays for each of the three strings
#tax = gen_accent_category("Cumbria", "English", "Southern")
#print(tax)

# list any strings not found in taxonomy.json
#get_new_country_strings("VCTK_output.csv")

# generate the accent string for a single accent
#res = gen_accent_string("Cumbria", "English", "Unknown")
#if res:
#    print(res)

# list all gender strings not found for given file
get_new_gender_strings("../SimpleVouceResample/16kHz_output.csv")

# take a csv and restructure it to unify region accent and country, as well as standardise gender
# restructure_csv("voxforge_output.csv", "voxforge_restructured.csv")