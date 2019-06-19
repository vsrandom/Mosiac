# Program for assignment 2
# Import modules
import numpy as np
import cv2
#from image_functions import *
import sys, os
import argparse
import imutils
from imutils import paths
from matplotlib import pyplot as plt
np.set_printoptions(precision=4)
#----------------------------------------------------------------------------------
# Construct the argument parser and parse the arguments.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image_dir", type=str, required=True, help="path to input directory of image with disparity")
ap.add_argument("-o", "--output_dir", type=str, required=True, help="path to the output image")
ap.add_argument("-a", "--apply", type=str, required=True, help="path to the other image on which to apply blur disparity")
args = vars(ap.parse_args())

# Grab the paths to the input images and initialize our images list
print("[INFO] loading images...")
paths = sorted(list(paths.list_images(args["image_dir"])))
other_path = args["apply"]
output_dir = args["output_dir"]

disp_path = ""
img_path = ""
for path in paths:
    if "disp" in path:
        disp_path = path
    elif "im" in path:
        img_path = path

# Loading
img = cv2.imread(img_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
disp = cv2.imread(disp_path)
disp = cv2.cvtColor(disp, cv2.COLOR_BGR2GRAY)

print('disparity range:' ,disp.reshape((img.shape[0]*img.shape[1], 1)).min(axis=0), disp.reshape((img.shape[0]*img.shape[1], 1)).max(axis=0))

img2 = cv2.imread(other_path)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

# Gives the blur radius given depth
def get_blur_radius(disparity):
    blur_radius = int(-0.1490196 * disparity + 39)
    if blur_radius % 2 == 0:
        blur_radius += 1
    return blur_radius

# Gives the mask for the given range of disparities
def get_mask(img, init, fin):
    mask = cv2.inRange(img, init, fin)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    return mask

# Shifts the mask at depth by its disparity value
def shift_mask(mask, disparity, factor=4, right=True):
    shift = int(disparity / factor)
    rows, cols, depth = mask.shape
    if right:
        shift = -shift
    M = np.float32([[1, 0, shift], [0, 1, 0]])
    mask = cv2.warpAffine(mask, M, (cols, rows))
    return mask

# Gives the defocused image given disparity map
def get_defocused_image(img, disp, factor=4, other=False, right=True):
    result = img[:]
    for i in range(0, 256):
        blur_radius = get_blur_radius(i)
        blurred_img = cv2.GaussianBlur(img, (blur_radius, blur_radius), 0)
        mask = get_mask(disp, i, i)
        if other:
            mask = shift_mask(mask, i, factor=factor, right=right)
        result = np.where(mask == (255, 255, 255), blurred_img, result)
    return result

# Gives the relative blur parameter which is proportional to blur radius
def get_relative_blur_parameter(blur1, blur2):
    rows, cols, depth = blur1.shape
    gray1 = cv2.cvtColor(blur1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(blur2, cv2.COLOR_BGR2GRAY)
    relative_blur = gray1[:]
    relative_blur[:] = (np.ceil(np.abs(np.sqrt(np.square(gray1) - np.square(gray2))))) * 10
    #relative_blur.reshape((relative_blur.shape[0] * relative_blur.shape[1], 1))
    return relative_blur


print("Getting defocused image (1/3)")
result1 = get_defocused_image(img, disp, factor = 4)
print("Writing defocused image (1/3)")
cv2.imwrite("{}".format(output_dir + "/defocus1.png"), cv2.cvtColor(result1, cv2.COLOR_RGB2BGR))
print("Getting defocused image (2/3)")
result2 = get_defocused_image(img2, disp, factor = 4, other=True)
print("Writing defocused image (2/3)")
cv2.imwrite("{}".format(output_dir + "/defocus2.png"), cv2.cvtColor(result2, cv2.COLOR_RGB2BGR))
print("Getting relative blur parameter image (3/3)")
result3 = get_relative_blur_parameter(result1, result2)
print("Writing relative blur parameter image (3/3)")
cv2.imwrite("{}".format(output_dir + "/relative_blur.png"), result3)