import cv2
import numpy as np

import config

def inTransition(frame):
    distWhite = getAveDistWhite(frame)

    whiteThreshold = config.whiteThreshold

    if distWhite < whiteThreshold:

        return True

    else:

        return False

def getAveDistWhite(frame):
    l2norm = (frame - 255) ** 2
    return np.sum(l2norm) / (frame.shape[0] * frame.shape[1])