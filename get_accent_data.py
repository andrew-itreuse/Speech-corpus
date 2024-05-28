# iterate through csv, get gender, accent, country and region
# if not in list, add to list
# I wil manually go through the list
import csv

input = "output.csv"
gender_list = []
accent_list = []
country_list = []
region_list = []

with open(input) as f:
    csv_reader = csv.DictReader(f, delimiter=",")
    for row in csv_reader:
        gender = row["gender"]
        if gender not in gender_list:
            gender_list.append(gender)
        accent = row["accent"]
        if accent not in accent_list:
            accent_list.append(accent)
        country = row["country"]
        if country not in country_list:
            country_list.append(country)
        region = row["region"]
        if region not in region_list:
            region_list.append(region)

print("Set of genders: ")
print(gender_list)
print("set of accents: ")
print(accent_list)
print("Set of countries: ")
print(country_list)
print("Set of regions: ")
print(region_list)
