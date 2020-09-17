import numpy as np
import cv2
from clean import cleanFrame
from analyze import isGoodBase

img = cv2.imread('./testingIms/firstFrame.jpg')

cleanImg = cleanFrame(img)

cv2.imwrite('./testingIms/cleanedFirstFrame.jpg', cleanImg)

goodBase = isGoodBase(cleanImg)

print(goodBase)
