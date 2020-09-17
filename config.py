import argparse

outputWindowName = 'Live Feed'
captureWindowKeyword = 'AirServer'

checkResources = True
checkFeasibility = True
skill = 8 # 0-10 float scale

minGold = 600000
minElixir = 600000
minDarkElixir = 2000

overrideGold = 800000
overrideElixir = 800000
overrideDarkElixir = 10000

whiteThreshold = 290000000/1687500

avgFpsCacheLen = 10 # num frames to calculate over

overSizeBounding = 35

textAnalysisSize = (640,640) # w/h

resourcePositions = [
                        (92, 79, 100, 30), # x, y, w, h
                        (92, 111, 100, 30),
                        (92, 150, 100, 30)
                    ]