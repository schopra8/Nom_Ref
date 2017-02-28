#############################################
# Author: Sahil Chopra
# schopra8@stanford.edu

# Analysis as to overlap between Imagenet Classes
# and utterances.

#############################################

import os
import sys
import csv
import sets

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from caffe_classes import class_names

all_utterances = set()
obj_to_sub_cat = {}
obj_to_basic_cat = {}
obj_to_sup_cat = {}

# Extract object info
with open('../object_table.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    obj = (row['object_name'], row['object_ind'])
    obj_to_sub_cat[obj] = row['sub_category']
    obj_to_basic_cat[obj] = row['basic_category']
    obj_to_sup_cat[obj] = row['super_category']
    all_utterances.add(row['sub_category'])
    all_utterances.add(row['basic_category'])
    all_utterances.add(row['super_category'])


# Remove spaces from words in class names -- to match utterances
class_names_edited = [x.replace(" ", "").replace(",", ", ") for x in class_names]

num_intersection = 0
overlapping_utterances = {}
for u in list(all_utterances):
    for c in class_names_edited:
        if u in c:
            num_intersection += 1
            overlapping_utterances[u] = True
            print (u, c)

print "--------------"
print "Total Unique Utterances: {}".format(len(all_utterances))
print "Overlapping Utterances Overall: {}".format(num_intersection)
print "Overlapping Utterances Overall: {}".format(len(overlapping_utterances.keys()))
print "--------------"