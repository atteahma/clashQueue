#! usr/bin/env python

import config
from analyze import isGoodBase
from transition import inTransition
from clean import cleanFrame
from execute import executeAction
from timing import calculateFps

import cv2
import numpy as np

from desktopmagic.screengrab_win32 import getRectAsImage
from win32 import win32api
from win32 import win32gui
from win32 import win32console as win32con
import winGuiAuto

import timeit
import os
import sys

def main():
    restart = False

    # get config settings
    outputWindowName = config.outputWindowName
    captureWindowKeyword = config.captureWindowKeyword
    avgFpsCacheLen = config.avgFpsCacheLen

    # create window 
    cv2.namedWindow(outputWindowName)
    
    # identify capture window
    hwnd = winGuiAuto.findTopWindow(captureWindowKeyword)
    print(f'hwnd={hwnd}')

    alreadyAnalyzed = False
    frameNum = 0
    fpsCache = [-1 for _ in range(avgFpsCacheLen)]

    while True:

        # time runtime
        startTime = timeit.default_timer()

        # get corner coordinates of capture window
        position = win32gui.GetWindowRect(hwnd)

        # save pixels into array
        frame = getRectAsImage(position)
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # clean frame
        frame = cleanFrame(frame)

        infoFrame = frame.copy()

        # check if is in transition
        isInTransition = inTransition(frame)
        if isInTransition:
            cv2.putText(img=infoFrame,
                        text='In Transition',
                        org=(20,infoFrame.shape[0]//2),
                        fontFace=0,
                        fontScale=2,
                        color=(0,0,255),
                        thickness=2
                        )
            print('[INFO] in transition')
        else:
            cv2.putText(img=infoFrame,
                        text='Base',
                        org=(20,infoFrame.shape[0]//2),
                        fontFace=0,
                        fontScale=2,
                        color=(0,255,0),
                        thickness=2
                        )
            print('[INFO] in base')

        # check if analysis already done
        if alreadyAnalyzed and (not isInTransition):
            alreadyAnalyzed = False
        
        # run analysis
        if not alreadyAnalyzed:
            goodBase = isGoodBase(frame)
            alreadyAnalyzed = True

        # complete action
        executeAction(goodBase)

        # escape conditions
        key = cv2.waitKey(1)
        if key == 27: # escape
            break
        if key == 96: # tilde key
            restart = True
            break
        
        # calculate fps
        stopTime = timeit.default_timer()
        if (avgFps := calculateFps( startTime,
                                    stopTime,
                                    frameNum,
                                    avgFpsCacheLen,
                                    fpsCache
                                )
        ): print(f'avgFps={avgFps}')

        # preview frame
        cv2.imshow(outputWindowName, infoFrame)

        frameNum += 1

    # cleanup
    cv2.destroyWindow(outputWindowName)

    return restart

if __name__ == '__main__':
    restart = main()
    # if restart:
    #     os.execv(__file__, sys.argv)