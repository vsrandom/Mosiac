import sys
import os
import cv2
import numpy as np
cwd = os.getcwd()

rimg = cv2.imread(cwd+'/upload/'+sys.argv[2])
rimg_gray = cv2.cvtColor(rimg,cv2.COLOR_BGR2GRAY)

limg = cv2.imread(cwd+'/upload/'+sys.argv[1])
limg_gray = cv2.cvtColor(limg,cv2.COLOR_BGR2GRAY)

sift = cv2.xfeatures2d.SIFT_create()

kp1, des1 = sift.detectAndCompute(rimg_gray,None)
kp2, des2 = sift.detectAndCompute(limg_gray,None)

bf=cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
matches = bf.match(des1,des2)
matches = sorted(matches,key=lambda x:x.distance)

matching_result = cv2.drawMatches(rimg_gray,kp1,limg_gray,kp2,matches[:20],None,flags=2)

good = []
for m in matches[:20]:
    good.append(m)

src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
M,mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
h,w = rimg_gray.shape

pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
dst=cv2.perspectiveTransform(pts,M)

final_image=cv2.warpPerspective(rimg,M,(limg.shape[1]+rimg.shape[1],limg.shape[0]))
final_image[0:limg.shape[0],0:limg.shape[1]]=limg

cv2.imwrite('stiched_image.jpg',final_image)

print('Image Saved')
sys.stdout.flush()