#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from glob import glob
import csv
import eyed3 
from pathlib import Path
import os


# In[ ]:


p = Path("output.csv")
if p.exists:
    os.remove(p)


# In[ ]:


data_dir = '/mnt/big-drive-2001-gp3/data/Tateoba/tatoeba_audio_eng/audio/'


# In[ ]:


# Import DictWriter class from CSV module
from csv import DictWriter
fieldname = ["database", "source", "format", "audioFileName", "audioPath", "transcript",
 "aligned", "sampling", "recording_device", "bitrate", "channels", "precision", "encoding", "date",
 "age", "gender", "accent", "country", "region", "user_name"]


# In[ ]:


def import_data(folder, speaker_gender, speaker_accent, speaker_country, speaker_region,user_name):
    audio_files= glob(data_dir +folder + '/*.mp3')
    for file in range(0, len(audio_files), 1):
        try:
            audiofile = eyed3.load(audio_files[file])
            dict = { 'database':'Tatoeba',
                                'source': 'Tatoeba',
                                'format': 'mp3',
                               'audioFileName':audio_files[file],
                               'audioPath':'/mnt/big-drive-2001-gp3/data/Tateoba/tatoeba_audio_eng/audio/'+ folder,
                               'transcript':audiofile.tag.title,
                               'aligned':True,
                               'sampling':audiofile.info.sample_freq,
                               'recording_device':'unkown',
                                'bitrate':audiofile.info.bit_rate[1],
                                'channels':'1',
                                'precision':'unknown',
                                'encoding':'unknown',
                                'date':'unknown',
                                'age':'unknown',
                                'gender':speaker_gender,
                                'accent':speaker_accent,
                                'country': speaker_country,
                                'region':speaker_region,
                                'user_name':user_name
                               }
            transcript ={
                 'transcript':audiofile.tag.title
            }
            
            # Open your CSV file in append mode
            # Create a file object for this file
            with open('output.csv', 'a') as f_object:
                # Pass the file object and a list 
                # of column names to DictWriter()
                # You will get a object of DictWriter
                dictwriter_object = DictWriter(f_object, fieldnames=fieldname)

                #Pass the dictionary as an argument to the Writerow()
                dictwriter_object.writerow(dict)

                #Close the file object
                f_object.close()
                
        except:
            pass

            


# In[ ]:


# import for all folders
import_data("BE","Male","English","British Accent","UK","BE")
print('BE')


import_data('CK', "Male", "American English", "US", "unknown","CK")
print("CK ")

import_data("Delian", "Female", "American English", "US", "California","Delian")
print("Delian")

import_data("Susan1430", "Female", "British English", "UK", "unknown","Susan1430")
print("Susan1430")

import_data("pencil", "Female", "English", "unknown", "unknown","pencil")
print("pencil")

import_data("rhys_mcg", "Male", "Australian English", "Australia", "none","rhys_mcg")
print("rhys_mcg")


# In[ ]:




