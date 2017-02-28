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

def substring_utterance_overlap(all_utterances, class_names_edited):
    num_intersection = 0
    overlapping_utterances = {}
    for u in list(all_utterances):
        for c in class_names_edited:
            if u in c:
                num_intersection += 1
                overlapping_utterances[u] = True
                print (u, c)

    print "--------------"
    print "Substring Overlap"
    print "Total Unique Utterances: {}".format(len(all_utterances))
    print "Intersection Utterances Overall: {}".format(num_intersection)
    print "Unique Overlapping Utterances Overall: {}".format(len(overlapping_utterances.keys()))
    print "--------------"

def exact_string_overlap(all_utterances, class_names, utterance_to_obj_and_cat):
    # Split multi word labels into individual words & remove whitespace
    class_names_edited = [x.replace(" ", "") for labels in class_names for x in str.split(labels, ",")]

    num_intersection = 0
    overlapping_utterances = {}
    for u in list(all_utterances):
        for c in class_names_edited:
            if u == c:
                num_intersection += 1
                overlapping_utterances[u] = True
                print "Utterance: {}, Imagenet Class: {}, {}".format(u, c, utterance_to_obj_and_cat[u])

    print "--------------"
    print "Exact String Overlap:"
    print "Total Unique Utterances: {}".format(len(all_utterances))
    print "Intersection Utterances Overall: {}".format(num_intersection)
    print "Unique Overlapping Utterances Overall: {}".format(len(overlapping_utterances.keys()))
    print "--------------"   

if __name__ == '__main__':
    all_utterances = set()
    utterance_to_obj_and_cat = {}

    # Extract object info
    with open('../object_table.csv') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        obj = (row['object_name'], row['object_ind'])

        utterance_to_obj_and_cat[row['sub_category']] = (obj, 'sub')
        utterance_to_obj_and_cat[row['basic_category']] = (obj, 'basic')  
        utterance_to_obj_and_cat[row['super_category']] = (obj, 'super')

        all_utterances.add(row['sub_category'])
        all_utterances.add(row['basic_category'])
        all_utterances.add(row['super_category'])

    substring_utterance_overlap(all_utterances, class_names)
    print "-----------------------------------------"
    exact_string_overlap(all_utterances, class_names, utterance_to_obj_and_cat)
