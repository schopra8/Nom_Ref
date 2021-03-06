################################################################################
#Michael Guerzhoy and Davi Frossard, 2016
#AlexNet implementation in TensorFlow, with weights
#Details: 
#http://www.cs.toronto.edu/~guerzhoy/tf_alexnet/
#
#With code from https://github.com/ethereon/caffe-tensorflow
#Model from  https://github.com/BVLC/caffe/tree/master/models/bvlc_alexnet
#Weights from Caffe converted using https://github.com/ethereon/caffe-tensorflow
#
#
#
# Edited by Sahil Chopra (schopra8@stanford.edu) for Nominal Reference
# Game Dataset.
################################################################################
# Modifications to Allow Usage w/out GUI
import matplotlib
matplotlib.use('Agg')

import urllib
import time
import glob
import os
import csv
import json
from numpy import *
from pylab import *
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from scipy.misc import imread
from scipy.misc import imresize
import matplotlib.image as mpimg
from scipy.ndimage import filters

import tensorflow as tf
from caffe_classes import class_names

from os.path import basename
from os.path import splitext

train_x = zeros((1, 227,227,3)).astype(float32)
train_y = zeros((1, 1000))
xdim = train_x.shape[1:]
ydim = train_y.shape[1]

################################################################################
#Read Image -- Test Imgs from Pre-Trained Data Set
# im1 = (imread("./test_imgs/poodle.png")[:,:,:3]).astype(float32)
# im1 = im1 - mean(im1)

# im2 = (imread("./test_imgs/laska.png")[:,:,:3]).astype(float32)
# im2 = im2 - mean(im2)

# Read object list
object_name_to_ind = {}
with open('../object_table.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    object_name_to_ind[row['object_name']] = row['object_ind']

# Read Images - Nominal Reference Game Images
nom_ref_img_names = []
nom_ref_imgs = []
img_to_object = {}
imgs_dir = '../imgs/nom_ref_imgs/scaled'
imgs_path = '{}/*.jpg'.format(imgs_dir)
for img_file in glob.glob(imgs_path):
  img = (imread(img_file)[:,:,:3]).astype(np.float32)
  img = img - mean(img)

  nom_ref_img_names.append(img_file)
  nom_ref_imgs.append(img)
 
  img_file_prefix = splitext(basename(img_file))[0].lower()
  obj_name = img_file_prefix[:img_file_prefix.find('_')]

  img_to_object[img_file] = (obj_name, object_name_to_ind[obj_name])


################################################################################

# (self.feed('data')
#         .conv(11, 11, 96, 4, 4, padding='VALID', name='conv1')
#         .lrn(2, 2e-05, 0.75, name='norm1')
#         .max_pool(3, 3, 2, 2, padding='VALID', name='pool1')
#         .conv(5, 5, 256, 1, 1, group=2, name='conv2')
#         .lrn(2, 2e-05, 0.75, name='norm2')
#         .max_pool(3, 3, 2, 2, padding='VALID', name='pool2')
#         .conv(3, 3, 384, 1, 1, name='conv3')
#         .conv(3, 3, 384, 1, 1, group=2, name='conv4')
#         .conv(3, 3, 256, 1, 1, group=2, name='conv5')
#         .fc(4096, name='fc6')
#         .fc(4096, name='fc7')
#         .fc(1000, relu=False, name='fc8')
#         .softmax(name='prob'))


net_data = load("bvlc_alexnet.npy").item()

def conv(input, kernel, biases, k_h, k_w, c_o, s_h, s_w,  padding="VALID", group=1):
    '''From https://github.com/ethereon/caffe-tensorflow
    '''
    c_i = input.get_shape()[-1]
    assert c_i%group==0
    assert c_o%group==0
    convolve = lambda i, k: tf.nn.conv2d(i, k, [1, s_h, s_w, 1], padding=padding)
    
    
    if group==1:
        conv = convolve(input, kernel)
    else:
        input_groups = tf.split(3, group, input)
        kernel_groups = tf.split(3, group, kernel)
        output_groups = [convolve(i, k) for i,k in zip(input_groups, kernel_groups)]
        conv = tf.concat(3, output_groups)
    return  tf.reshape(tf.nn.bias_add(conv, biases), [-1]+conv.get_shape().as_list()[1:])



x = tf.placeholder(tf.float32, (None,) + xdim)


#conv1
#conv(11, 11, 96, 4, 4, padding='VALID', name='conv1')
k_h = 11; k_w = 11; c_o = 96; s_h = 4; s_w = 4
conv1W = tf.Variable(net_data["conv1"][0])
conv1b = tf.Variable(net_data["conv1"][1])
conv1_in = conv(x, conv1W, conv1b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=1)
conv1 = tf.nn.relu(conv1_in)

#lrn1
#lrn(2, 2e-05, 0.75, name='norm1')
radius = 2; alpha = 2e-05; beta = 0.75; bias = 1.0
lrn1 = tf.nn.local_response_normalization(conv1,
                                                  depth_radius=radius,
                                                  alpha=alpha,
                                                  beta=beta,
                                                  bias=bias)

#maxpool1
#max_pool(3, 3, 2, 2, padding='VALID', name='pool1')
k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
maxpool1 = tf.nn.max_pool(lrn1, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)


#conv2
#conv(5, 5, 256, 1, 1, group=2, name='conv2')
k_h = 5; k_w = 5; c_o = 256; s_h = 1; s_w = 1; group = 2
conv2W = tf.Variable(net_data["conv2"][0])
conv2b = tf.Variable(net_data["conv2"][1])
conv2_in = conv(maxpool1, conv2W, conv2b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
conv2 = tf.nn.relu(conv2_in)


#lrn2
#lrn(2, 2e-05, 0.75, name='norm2')
radius = 2; alpha = 2e-05; beta = 0.75; bias = 1.0
lrn2 = tf.nn.local_response_normalization(conv2,
                                                  depth_radius=radius,
                                                  alpha=alpha,
                                                  beta=beta,
                                                  bias=bias)

#maxpool2
#max_pool(3, 3, 2, 2, padding='VALID', name='pool2')                                                  
k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
maxpool2 = tf.nn.max_pool(lrn2, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)

#conv3
#conv(3, 3, 384, 1, 1, name='conv3')
k_h = 3; k_w = 3; c_o = 384; s_h = 1; s_w = 1; group = 1
conv3W = tf.Variable(net_data["conv3"][0])
conv3b = tf.Variable(net_data["conv3"][1])
conv3_in = conv(maxpool2, conv3W, conv3b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
conv3 = tf.nn.relu(conv3_in)

#conv4
#conv(3, 3, 384, 1, 1, group=2, name='conv4')
k_h = 3; k_w = 3; c_o = 384; s_h = 1; s_w = 1; group = 2
conv4W = tf.Variable(net_data["conv4"][0])
conv4b = tf.Variable(net_data["conv4"][1])
conv4_in = conv(conv3, conv4W, conv4b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
conv4 = tf.nn.relu(conv4_in)


#conv5
#conv(3, 3, 256, 1, 1, group=2, name='conv5')
k_h = 3; k_w = 3; c_o = 256; s_h = 1; s_w = 1; group = 2
conv5W = tf.Variable(net_data["conv5"][0])
conv5b = tf.Variable(net_data["conv5"][1])
conv5_in = conv(conv4, conv5W, conv5b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
conv5 = tf.nn.relu(conv5_in)

#maxpool5
#max_pool(3, 3, 2, 2, padding='VALID', name='pool5')
k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
maxpool5 = tf.nn.max_pool(conv5, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)

#fc6
#fc(4096, name='fc6')
fc6W = tf.Variable(net_data["fc6"][0])
fc6b = tf.Variable(net_data["fc6"][1])
fc6 = tf.nn.relu_layer(tf.reshape(maxpool5, [-1, int(prod(maxpool5.get_shape()[1:]))]), fc6W, fc6b)

#fc7
#fc(4096, name='fc7')
fc7W = tf.Variable(net_data["fc7"][0])
fc7b = tf.Variable(net_data["fc7"][1])
fc7 = tf.nn.relu_layer(fc6, fc7W, fc7b)

#fc8
#fc(1000, relu=False, name='fc8')
fc8W = tf.Variable(net_data["fc8"][0])
fc8b = tf.Variable(net_data["fc8"][1])
fc8 = tf.nn.xw_plus_b(fc7, fc8W, fc8b)


#prob
#softmax(name='prob'))
prob = tf.nn.softmax(fc8)

init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

t = time.time()
# output = sess.run(prob, feed_dict = {x:[im1,im2]})

# Retrieve probabilities only
# output = sess.run(prob, feed_dict = {x:nom_ref_imgs})

# Retrieve probabilities and vectors
output = sess.run({"prob": prob, "fc8": fc8}, feed_dict = {x:nom_ref_imgs})

################################################################################

# Create results directory
results_dir = './alexnet_output/nom_ref'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Output csv of all predicted labels:
predicted_labels_file = '{}/predicted_labels.csv'.format(results_dir)
with open(predicted_labels_file ,'wb') as f:
  writer = csv.writer(f)
  writer.writerow(["File Name", "Object", "Object_Index", "Label", "Probability"])
  for input_im_ind in range(output["prob"].shape[0]):
      inds = argsort(output["prob"])[input_im_ind,:]
      print "Predicting Image", input_im_ind
      img_file_name = nom_ref_img_names[input_im_ind]
      for i in range(10):
        vals = [img_file_name, img_to_object[img_file_name][0], img_to_object[img_file_name][1], class_names[inds[-1-i]], output["prob"][input_im_ind, inds[-1-i]]]
        writer.writerow(vals)

# Output Top 10 Labels Per Object
top_10_labels_file = '{}/top_10_labels.csv'.format(results_dir)
with open(top_10_labels_file ,'wb') as f:
  writer = csv.writer(f)
  header = ["Object", "Object_Index"]
  header = ["Label {}".format(i+1) for i in xrange(10)]
  header.insert(0, "Object_Index")
  header.insert(0, "Object")
  writer.writerow(header)

  for input_im_ind in range(output["prob"].shape[0]):
      inds = argsort(output["prob"])[input_im_ind,:]
      print "Predicting Image", input_im_ind
      img_file_name = nom_ref_img_names[input_im_ind]
      obj = img_to_object[img_file_name]

      label_prob_pairs = ["{} ({})".format(class_names[inds[-1-i]], output["prob"][input_im_ind, inds[-1-i]]) for i in xrange(10)]
      vals = [obj[0], obj[1]]
      vals.extend(label_prob_pairs)
      writer.writerow(vals)

# Output Tensor:
embeddings_file = '{}/embeddings.json'.format(results_dir)
embeddings = {}
for input_im_ind in range(output["fc8"].shape[0]):
  img_file_name = nom_ref_img_names[input_im_ind]
  obj_index = img_to_object[img_file_name][1]
  embeddings[obj_index] = output["fc8"][input_im_ind, :].tolist()

with open(embeddings_file, 'w') as fp:
    json.dump(embeddings, fp)

print time.time()-t
