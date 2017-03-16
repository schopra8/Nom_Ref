#############################################
# Author: Sahil Chopra
# schopra8@stanford.edu

# Image Scraping for Generalization Task Type 1
#############################################
import httplib
import urllib
import base64
import csv
import json
import os

OBJECT_TABLE_FILE = '../object_table.csv'
TASK1_IMGS_DIR = '../imgs/generalization_task_1_general_scraped'
IMG_URLS_SUMMARY_FILE = 'img_urls_summary.csv'
NUM_SCRAPE_IMGS = 50

class Utterance_Category(object):
    SUB = 'sub'
    BASIC = 'basic'
    SUP = 'super'

def load_obj_utterance_mappings():
    """ Read the object table file.
        Returns mappings from object_index to subordinate uttereance,
        superordinate utterance, and basic utterance.
    """
    obj_idx_to_sub_utterance = {}
    obj_idx_to_basic_utterance = {}
    obj_idx_to_sup_utterance = {}

    with open(OBJECT_TABLE_FILE, 'rb') as fn:
        reader = csv.DictReader(fn)
        for r in reader:
            obj_idx = int(r['object_ind'])
            obj_idx_to_sub_utterance[obj_idx] = r['sub_category']
            obj_idx_to_basic_utterance[obj_idx] = r['basic_category']
            obj_idx_to_sup_utterance[obj_idx] = r['super_category']

    return obj_idx_to_sub_utterance, obj_idx_to_basic_utterance, obj_idx_to_sup_utterance

def scrape_images(idx_to_utterance, utterance_category):
    """ Given a mapping of object idexes to utterances, search
        for the given images on a white background and save the top
        NUM_SCRAPE_IMG results.
    """
    print "-" * 80
    print "Scraping {} Images".format(utterance_category)
    print "-" * 80
    for obj_idx, utterance in idx_to_utterance.iteritems():
        save_dir = '{}/{}/{}'.format(TASK1_IMGS_DIR, utterance_category, str(obj_idx))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        print "Scraping Images for Utterance {}".format(utterance)
        scrape_images_for_utterance(obj_idx, utterance, utterance_category, save_dir)

def scrape_images_for_utterance(obj_idx, utterance, utterance_category, save_dir):
    """ Seach for the term "{utterance} on white background".
        Save top NUM_SCRAPE_IMG results for this query.
    """
    try:
        data = make_bing_request(utterance)
        img_urls = parse_bing_response(data)
        img_urls_summary_fn = '{}/{}'.format(save_dir, IMG_URLS_SUMMARY_FILE)
        with open(img_urls_summary_fn, 'wb') as img_urls_fn:
            writer = csv.writer(img_urls_fn)
            header = ["img_index", "img_url"]
            writer.writerow(header)
            for i, img_url in enumerate(img_urls):
                save_file = '{}/img_{}.jpeg'.format(save_dir, i)
                urllib.urlretrieve(img_url, save_file)
                writer.writerow([i, img_url])

    except Exception as e:
        print "Failed to retrieve images for utterance: {}".format(utterance)

def make_bing_request(utterance):
    """ Make a request to Bing's Search API for images of the given utterance.

        Note: Checkout the below link to learn how to use the Microsoft Bing Image Search API
        https://dev.cognitive.microsoft.com/docs/services/56b43f0ccf5ff8098cef3808/operations/56b4433fcf5ff8098cef380c
    """
    headers = {
        # Note that this key only lasts 90-Days on a Free Trial
        # Key Acquired: March 10, 2017
        'Ocp-Apim-Subscription-Key': '',
    }

    params = urllib.urlencode({
        'q': '"{}"'.format(utterance),
        'count': '20',
        'offset': '0',
        'mkt': 'en-us',
        'safeSearch': 'Moderate',
    })

    try:
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/images/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
    except Exception as e:
        raise e

def parse_bing_response(data):
    """ Parse the response from the GET request to Bing.
        Returns a list of [img_url]
    """
    try:
        data_loaded = json.loads(data)
        imgs = [img_metadata["contentUrl"] for img_metadata in data_loaded["value"]]
        return imgs
    except Exception as e:
        raise e

def main():
    sub_utt_mapping, basic_utt_mapping, sup_utt_mapping = load_obj_utterance_mappings()
    scrape_images(sub_utt_mapping, Utterance_Category.SUB)

if __name__ == '__main__':
    main()
