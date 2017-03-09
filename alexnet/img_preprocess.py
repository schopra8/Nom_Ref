#############################################
# Author: Sahil Chopra
# schopra8@stanford.edu

# According to the Alexnet paper, all images inputted
# to their system were 256 x 256. They took images and scaled
# them so that the shorter side of the image was of length 256.
# Then cropped the image so that they extracted the central
# patch of 256 x 256 pixels.

# Goal: Preprocess nominal reference images so that they
# are of the appropriate 256 x 256 size.

# NOTE: While the paper uses 256 x 256 images, the given
# code uses 227 x 227 images.

#############################################
import glob
import numpy as np
from subprocess import call
from math import ceil
import os
from os.path import basename
from os.path import splitext
from scipy.misc import imread
from scipy.misc import imresize
from scipy.misc import imsave

IMG_SIZE = 227.0
BACKGROUND_COLOR = 255 # White

def get_min_dim(im):
    # Determine minimum when examining width and height of an image
    # Returns minimm dimension and True (if height is min dim)
    # or False (if width is min dim)
    if im.shape[0] < im.shape[1]:
        return im.shape[0], True
    else:
        return im.shape[1], False

def get_max_dim(im):
    # Determine max when examining width and height of an image
    # Returns max dimension and True (if height is max dim)
    # or False (if width is max dim)
    if im.shape[0] > im.shape[1]:
        return im.shape[0], True
    else:
        return im.shape[1], False    

def upscale_by_smaller_dim(im):
    # Upscale image, if one of the dimensions is less than IMG_SIZE
    min_dim, height_is_min = get_min_dim(im)
    if min_dim < IMG_SIZE:
        upsample_percentage = (IMG_SIZE / min_dim)
        if height_is_min:
            width_scaled = int(im.shape[1] * upsample_percentage)
            rescaled_shape = (int(IMG_SIZE), width_scaled)
        else:
            height_scaled = int(im.shape[0] * upsample_percentage)
            rescaled_shape = (height_scaled, int(IMG_SIZE))
        im = imresize(im, rescaled_shape)

    print "Image Dimensions after Upscaling"
    print im.shape
    return im

def upscale_by_larger_dim(im):
    # Upscale image, if the larger of the dimensions is smaller than IMG_SIZE
    max_dim, height_is_max = get_max_dim(im)
    if max_dim < IMG_SIZE:
        upsample_percentage = (IMG_SIZE / max_dim)
        if height_is_max:
            width_scaled = int(im.shape[1] * upsample_percentage)
            rescaled_shape = (int(IMG_SIZE), width_scaled)
        else:
            height_scaled = int(im.shape[0] * upsample_percentage)
            rescaled_shape = (height_scaled, int(IMG_SIZE))
        im = imresize(im, rescaled_shape)

    print "Image Dimensions after Upscaling"
    print im.shape
    return im

def resize_by_smaller_dim(im):
    # Resize image such that smaller length is IMG_SIZE
    min_dim, height_is_min = get_min_dim(im)
    if min_dim != IMG_SIZE:
        downsample_frac = (IMG_SIZE / min_dim)
        im = imresize(im, downsample_frac)

    print "Image Dimensions after Resizing"
    print im.shape    
    return im

def resize_by_larger_dim(im):
    # Resize image such that larger length is IMG_SIZE
    max_dim, height_is_max = get_max_dim(im)
    if max_dim != IMG_SIZE:
        downsample_frac = (IMG_SIZE / max_dim)
        im = imresize(im, downsample_frac)

    print "Image Dimensions after Resizing"
    print im.shape    
    return im

def crop_center(im):
    # Extract central IMG_SIZE x IMG_SIZE portion of the image
    min_dim, height_is_min = get_min_dim(im)
    if height_is_min:
        if im.shape[1] > IMG_SIZE:
            margin = int((im.shape[1] - IMG_SIZE)/2)
            # If margin is 0, we have 1 pixel to chop off
            # If we follow through with cropping, we'll
            # end up with a side that has length 0.
            if margin != 0:
                im = im[:, margin : - margin, :]
    else:
        if im.shape[0] > IMG_SIZE:
            margin = int((im.shape[0] - IMG_SIZE)/2)
            # If margin is 0, we have 1 pixel to chop off
            # If we follow through with cropping, we'll
            # end up with a side that has length 0.
            if margin != 0:
                im = im[margin : -margin, :, :]

    print "Image Dimensions after Cropping"
    print im.shape
    return im

def pad_with_whitespace(im):
    # Pad image with white space to make it of size
    # IMG_SIZE x IMG_SIZE (with an error of potentially +1)
    if im.shape[0] <  IMG_SIZE:
        pad_width = int(ceil((IMG_SIZE - im.shape[0])/2))
        npad = ((pad_width, pad_width), (0, 0), (0,0))
        im = np.pad(im, pad_width=npad, mode='constant', 
            constant_values=BACKGROUND_COLOR)
    if im.shape[1] < IMG_SIZE:
        pad_width = int(ceil(IMG_SIZE - im.shape[1]))
        npad = ((0, 0), (pad_width, pad_width), (0,0))
        im = np.pad(im, pad_width=npad, mode='constant', 
            constant_values=BACKGROUND_COLOR)
    print "Image Dimensions after Adding White Space"
    print im.shape    
    return im

def crop_post_processing(im):
    # If we have an odd number of pixels for height or width
    # we will be left with an extra row or column of pixels
    # i.e. IMG_SIZE x IMG_SIZE + 1 or
    # IMG_SIZE + 1 x 256. We must get rid of this
    # excess -- as Alexnet requires a fixed input of
    # IMG_SIZE x IMG_SIZE images.
    if im.shape[0] > IMG_SIZE:
        im = im[0:IMG_SIZE, :, :]
    if im.shape[1] > IMG_SIZE:
        im = im[:, 0:IMG_SIZE, :]
    return im

def preprocess_imgs(orig_imgs_dir, scaled_imgs_dir, resize_for_smaller_dim=True):
    # Given the path to a directory of jpg images, open each image in the dir
    # and resize the images to create IMG_SIZE x IMG_SIZE patches. Then place
    # these images in another scaled_imgs_dir.

    # If resize_for_smaller_dim is True scale the images such that the smaller 
    # dimension is IMG_SIZE and then crop the center of image to create the image patch.
    # This is what is mentioned in the Alexnet paper. 

    # Else, scale the image such that the larger dimensions is IMG_SIZE and then fill
    # the rest of the image with white space in order to create the image patch.
    imgs = {}

    orig_imgs_path = '{}/*.jpg'.format(orig_imgs_dir)
    for orig_img_file in glob.glob(orig_imgs_path):
        print "-----------------------------------"
        print "Processing {}".format(orig_img_file)

        scaled_img_file = '{}_scaled.jpg'.format(splitext(basename(orig_img_file))[0])
        im = (imread(orig_img_file)[:,:,:3]).astype(np.float32)

        print "Original Image Dimensions"
        print im.shape

        if resize_for_smaller_dim:
            # Upsample if smaller dimension < IMG_SIZE
            im = upscale_by_smaller_dim(im)

            # Downsample such that smaller dimension = IMG_SIZE
            im = resize_by_smaller_dim(im)

        else:
            # Upsample if larger dimension < IMG_SIZE
            im = upscale_by_larger_dim(im)

            # Downsample such that the larger dimension = IMG_SIZE
            im = resize_by_larger_dim(im)

            # Add white space to create a IMG_SIZE x IMG_SIZE patch
            im = pad_with_whitespace(im)

        # Crop image if necessary (sometimes we have a dimension
        # of IMG_SIZE + 1 -- due to rounding up when we pad an image
        # that previously had an odd number of pixels
        im = crop_center(im)
        im = crop_post_processing(im)

        # Ensue correct dimensions of the image
        assert(im.shape == (IMG_SIZE, IMG_SIZE, 3)) 

        print "Finished Image"
        print im.shape
        print "-----------------------------------"

        # Store scaled image
        imgs[scaled_img_file] = im

    # Save scaled images
    for name, im in imgs.iteritems():
        fp = '{}/{}'.format(scaled_imgs_dir, name)
        imsave(fp, im)

# Excute Pre-Processing
orig_imgs_dir = '../imgs/nom_ref_imgs/orig'
scaled_imgs_dir = '../imgs/nom_ref_imgs/scaled'
if not os.path.exists(scaled_imgs_dir):
    os.makedirs(scaled_imgs_dir)
print "-----------------------------------"
print 'Scaling images from {} and deposting them in {}'.format(orig_imgs_dir, scaled_imgs_dir)
preprocess_imgs(orig_imgs_dir, scaled_imgs_dir, False)
print 'Scaling complete!'
print "-----------------------------------"



