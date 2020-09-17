import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
import time
import scipy.ndimage as spi

from config import *

def isGoodBase(frame):
    print(f'[INFO] into frame analysis dims: (w x h) {frame.shape[1]} x {frame.shape[0]}')

    # resource data (gold, elixir, dark elixir) (return now if low)
    (gold, elixir, darkElixir) = getResources(frame)
    
    if not goodResources(gold, elixir, darkElixir):
        return False

    # network to check if base is feasible (return if not feasible)

    return True

def getResources(frame):
    # new bounding box
    bottomCoord = frame.shape[0] // 2
    rightCoord = frame.shape[1] // 4

    croppedFrame = frame[:bottomCoord,:rightCoord]

    # OPTION 1:
    # bboxes = findText(croppedFrame) # get bounding boxes
    # OPTION 2:
    bboxes = resourcePositions

    text = getText(croppedFrame, bboxes) # array of the lines in the boxes

    resources = []
    for s in text:
        try:
            num = int(s.replace(',', ''))
            resources.append(num)
        except:
            continue
    
    return resources # gold, elixir, dark

def goodResources(gold, elixir, darkElixir):
    # check resources level 1
    if (gold > minGold) and (elixir > minElixir) and (darkElixir > minDarkElixir):
        return True

    # check if override conditions hold
    if (gold > overrideGold) or (elixir > overrideElixir) or (darkElixir > overrideDarkElixir):
        return True
    
    return False

def sharpen_single_channel(im):
    
    # convert to float representation
    im = im.astype(np.float) / 255

    # Sharpening Constant
    a = 2
    
    # Gaussian Constants
    k = 12
    s = 0.3 * (0.5 * (k-1) - 1) + 0.8
    
    # Create Gaussian Filter    
    gaussian_1d = cv2.getGaussianKernel(k, s)
    gaussian_2d = np.outer(gaussian_1d, gaussian_1d)
    gaussian_2d = gaussian_2d / np.sum(gaussian_2d)
    
    # Create Unit Impulse Filter
    unit_impulse = np.zeros((k,k))
    np.put(unit_impulse, unit_impulse.size//2, 1)
    
    # Create Compound Filter
    compound_filter = ((1 + a) * unit_impulse) - (a * gaussian_2d)

    # Convolve Image
    im_conv = spi.convolve(im, compound_filter)
    
    # Clip Image
    im_conv_clipped = np.clip(im_conv, 0, 1)

    return (im_conv_clipped * 255).astype(np.uint8)

def sharpen_three_channel(im):

    # Split Channels
    r = im[:,:,0]
    g = im[:,:,1]
    b = im[:,:,2]
    
    # Sharpen Channels
    r_sharpened = sharpen_single_channel(r)
    g_sharpened = sharpen_single_channel(g)
    b_sharpened = sharpen_single_channel(b)
    
    # Combine Channels
    im_sharpened = np.stack((r_sharpened, g_sharpened, b_sharpened), axis=2)
    
    return im_sharpened

def findText(image):

    # sharpen for hopefully better results??
    imageSharpened = sharpen_three_channel(image)
    testOut = np.vstack((image, imageSharpened))
    cv2.imwrite('./testingIms/testOutSharp.jpg', testOut)
    image = imageSharpened

    orig = image.copy()
    (H, W) = image.shape[:2]
    print(f'[INFO] into text analysis dims: (w x h) {image.shape[1]} x {image.shape[0]}')

    # define scale
    (newW, newH) = textAnalysisSize
    rW = W / float(newW)
    rH = H / float(newH)

    print(f'[INFO] during text analysis dims: (w x h) {newW} x {newH}')

    # resize image
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    layerNames = [
    "feature_fusion/Conv_7/Sigmoid",
    "feature_fusion/concat_3"]

    # load net
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet('frozen_east_text_detection.pb')

    # run net
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
    (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    print("[INFO] text detection took {:.6f} seconds".format(end - start))

    # get confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    MIN_CONFIDENCE = 0.5

    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over potentials
        for x in range(0, numCols):
            if scoresData[x] < MIN_CONFIDENCE:
                continue
            
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply nms
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # loop over bounding boxes
    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        # draw the bounding box on the image
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
    
    cv2.imwrite('./testingIms/bboxes.jpg', orig)

    restruct = lambda t: (t[0], t[1], t[2]-t[0], t[3]-t[1])

    return list(map(restruct, boxes))

def getText(img, bboxes):
    out = []
    testi = 0
    for bbox in bboxes:
        TLX, TLY, W, H = bbox
        imSlice = img[TLY:TLY+H, TLX:TLX+W]
        text = getTextSingle(imSlice, str(testi))
        out.append(text)
        testi += 1
    return out

def getTextSingle(img, salt):
    # OCR ALGO
    cv2.imwrite('./testingIms/bboxtest' + salt + '.jpg', img)
    return '200,000'
    