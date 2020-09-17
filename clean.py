import numpy as np
import cv2
from config import overSizeBounding

def cleanFrame(frame):
    # crop task bar and oversized bounding box
    frame = frame[100:, overSizeBounding:][:-1 * overSizeBounding, :-1 * overSizeBounding]

    # crop black borders
    frame = crop_image_only_outside(frame, tol=5)

    return frame

def crop_image_only_outside(img,tol=0):

    mask = img>tol
    if img.ndim==3:

        mask = mask.all(2)
    m,n = mask.shape

    mask0,mask1 = mask.any(0),mask.any(1)

    col_start,col_end = mask0.argmax(),n-mask0[::-1].argmax()
    row_start,row_end = mask1.argmax(),m-mask1[::-1].argmax()

    return img[row_start:row_end,col_start:col_end]

