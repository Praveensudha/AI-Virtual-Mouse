import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import os

"""
AI Virtual Mouse Control System
This script allows you to control your computer's mouse using hand gestures
captured through a webcam. Features include:
- Mouse movement using index finger
- Left-click using index and middle finger pinch
- Right-click using thumb and pinky finger pinch
"""

#############################
# Configuration parameters
wCam, hCam = 640, 480  # Camera resolution
frameR = 100  # Frame Reduction for better boundary control
smoothening = 7  # Mouse movement smoothing factor
##############################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
try:
    wScr, hScr = autopy.screen.size()
except Exception as e:
    print(f"Error getting screen size: {e}")
    exit()
while True:
    #1. Find hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #2. Get the tip of the index and the middle fingers
    if len(lmList)!=0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        #print(x1, y1, x2, y2)

    #3. Check which finger are up
        fingers = detector.fingersUp()
        #print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam-frameR, hCam-frameR), (255,0,255), 2)

    #4. Only index finger: Moving mode
        if fingers[1]==1 and fingers[2]==0:

            #5. Convert Coordinates
            x3 = np.interp(x1, (frameR,wCam-frameR), (0,wScr))
            y3 = np.interp(y1, (frameR,hCam-frameR), (0,hScr))

            #6. Smoothen Valuse
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            #7. Move mouse
            autopy.mouse.move(wScr-clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

    #8. Both index and middle are up: Left Clicking mode
        if fingers[1]==1 and fingers[2]==1 and fingers[4]==0:  # Make sure pinky is down for left click
            #9. Find distance between fingers 
            length, img, lineInfo = detector.findDistance(8, 12, img)
            
            #10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0,255,0), cv2.FILLED)
                autopy.mouse.click()

        #11. Index and pinky are up: Right Clicking mode
        if fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 1:  # Middle finger down, pinky up


             #12. Find distance between fingers 
            length, img, lineInfo = detector.findDistance(4, 20, img)
            print(length)
            
            #13. Click mouse if distance short
            if length< 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0,255,0), cv2.FILLED)
                autopy.mouse.click(button=autopy.mouse.Button.RIGHT)
    
    #14. Both index and pinky are up: Open A Drive mode
        if fingers[1] == 1 and fingers[2] == 1:
        #15. Find distance between fingers
            length, img, lineInfo = detector.findDistance(4, 16, img)
            print(length)

        #16. Open A Drive if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                

    
   
    #11. Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),3)
   
    #12. Display
    
    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1)  == 27:
        break
cap.release()
cv2.destroyAllWindows()  
