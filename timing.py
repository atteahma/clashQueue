def calculateFps(startTime, stopTime, frameNum, avgFpsCacheLen, fpsCache):
    fps = 1/(stopTime-startTime)
    fpsIndex = frameNum % avgFpsCacheLen
    fpsCache[fpsIndex] = fps
    if fpsIndex == (avgFpsCacheLen - 1):
        avgFps = sum(fpsCache) / avgFpsCacheLen
        return avgFps
    
    return None