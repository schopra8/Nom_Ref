#!/usr/bin/env python

#############################################
# Author: Sahil Chopra
# schopra8@stanford.edu
#
# Given a keyword, leverage the Bing API
# to search an download images. Maybe useful
# as a tool to those who want to harvest 
# collections of images for stimuli.
#
# Note: In order to interact with the Bing API
#       one must first acquire a Subscription Key.
#       See https://www.microsoft.com/cognitive-services/en-us/bing-web-search-api
#       for details.
#############################################

import httplib
import urllib
import base64
import csv
import json
import os

# Note: Must Acquire Indiviudal Subscription Key.
OCP_APIM_SUBSCRIPTION_KEY = ''
IMG_URLS_SUMMARY_FILE = 'img_urls_summary.csv'

def scrape_images(phrases, num_imgs, save_dir='./imgs'):
    """ Given a mapping of object idexes to phrases, search
        for the given images and save the top num_imgs results.
        Images are by default saved to the directory: {save_dir}/{obj_index}/ 
        Args:
            phrases = mapping[obj_index] -> "search phrase"
            num_imgs = # of images to download per 
                        search phrase
            save_dir = directory that you want save images to
    """
    for obj_idx, phrase in phrases.iteritems():
        phrase_save_dir = '{}/{}'.format(save_dir, str(obj_idx))
        if not os.path.exists(phrase_save_dir):
            os.makedirs(phrase_save_dir)
        print "Scraping Images for Phrase {}".format(phrase)
        scrape_images_by_phrase(obj_idx, phrase, phrase_save_dir, num_imgs)

def scrape_images_by_phrase(obj_idx, phrase, phrase_save_dir, num_imgs):
    """ Seach for the phrase.
        Save top num_imgs results for this query.
    """
    try:
        data = make_bing_request(phrase, num_imgs)
        img_urls = parse_bing_response(data)
        img_urls_summary_fn = '{}/{}'.format(phrase_save_dir, IMG_URLS_SUMMARY_FILE)
        with open(img_urls_summary_fn, 'wb') as img_urls_fn:
            writer = csv.writer(img_urls_fn)
            header = ["img_index", "img_url"]
            writer.writerow(header)
            for i, img in enumerate(img_urls):
                save_file = '{}/img_{}.{}'.format(phrase_save_dir, i, img[1])
                urllib.urlretrieve(img[0], save_file)
                writer.writerow([i, img[0]])

    except Exception as e:
        print "Failed to retrieve images for phrase: {}".format(phrase)

def make_bing_request(phrase, num_imgs):
    """ Make a request to Bing's Search API for images of the given search phrase.

        Note: Checkout the below link to learn how to use the Microsoft Bing Image Search API
        https://dev.cognitive.microsoft.com/docs/services/56b43f0ccf5ff8098cef3808/operations/56b4433fcf5ff8098cef380c
    """
    headers = {
        'Ocp-Apim-Subscription-Key': OCP_APIM_SUBSCRIPTION_KEY,
    }

    params = urllib.urlencode({
        'q': '{}'.format(phrase),
        'count': num_imgs,
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
        print e
        raise e

def parse_bing_response(data):
    """ Parse the response from the GET request to Bing.
        Returns a list of [(img_url, encoding_format)]
    """
    try:
        data_loaded = json.loads(data)
        imgs = [(img_metadata["contentUrl"], img_metadata["encodingFormat"]) for img_metadata in data_loaded["value"]]
        return imgs
    except Exception as e:
        print e
        raise e

def main():
    # Test Case
    scrape_images({0: 'cats'}, 5)

if __name__ == '__main__':
    main()
