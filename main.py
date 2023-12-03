import cv2
import os
import mediapipe as mp
import numpy as np
from cvzone.HandTrackingModule import HandDetector

#variables
width, height = 1280, 720 
folderPath = 'Presentation'
imgNumber = 0
s_width, s_height = 120, 90
# gesture_threshold = 300
left_fingers = [0, 0, 0, 0, 0]
right_fingers = [1, 1, 0, 0, 1]
button_pressed = False
count = 0
indexFinger = 0, 0
xp = 0
yp = 0
type = 0 #0:pointer mode, 1:slide switch mode, 2:nothing mode 
annotations = [[]]
annotation_count = -1
annotation_start = False

#Hand Detector
hand_detector = HandDetector(detectionCon = 0.5, maxHands = 2)

#camera setup
cap = cv2.VideoCapture(0)
# cap.set(3, width)
# cap.set(4, height)

#Get the list of presentation imgs
imgPath = sorted(os.listdir(folderPath), key=len)
print(imgPath)
while True:
    #Import imgs
    success, img = cap.read()
    h, w, _ = img.shape
    img = cv2.flip(img, 1)

    img_resized = cv2.resize(img, (s_width, s_height))
    imgPathFull = os.path.join(folderPath, imgPath[imgNumber])
    imgCurrent = cv2.imread(imgPathFull)
    imgCurrent_resized = cv2.resize(imgCurrent, (width, height))

    hands, img = hand_detector.findHands(img)
    # cv2.line(img, (0, gesture_threshold),(width, gesture_threshold), (0, 255, 0), 10)
    
    for hand in hands:
        if hand["type"] == "Right":
            right_fingers = hand_detector.fingersUp(hand) 
            if right_fingers == [0, 1, 0, 0, 1]: type = 0
            elif right_fingers == [1, 0, 0, 0, 1]: type = 1
            elif right_fingers == [1, 1, 0, 0, 1]: type = 2
            else: type = type 

        # Check if it's the left hand
        if hand["type"] == "Left":
            # Get information about the fingers of the left hand
                left_fingers = hand_detector.fingersUp(hand)
                lmlist = hand['lmList']
                xValue = int(np.interp(lmlist[8][0], [w//2, w-100], [0, width]))
                yValue = int(np.interp(lmlist[8][1], [100, h-100], [0, height]))
                indexFinger = xValue, yValue
                # print(indexFinger)
                if left_fingers == [0, 1, 0, 0, 0]:
                    annotation_start = False

    if len(hands) == 2 and type == 1:
            
            if right_fingers == [1, 0, 0, 0, 0]:
            # print("left: ",left_fingers)
            # print("right: ",right_fingers)
                if left_fingers == [1, 1, 0, 0, 0] and button_pressed == False and imgNumber>0:
                    button_pressed = True
                    imgNumber -= 1
                    print("LEFT, imgNumber: ", imgNumber)
                    count = 0
                    annotations = [[]]
                    annotation_count = -1
                    annotation_start = False

                elif left_fingers == [1, 1, 1, 0, 0] and button_pressed == False and imgNumber<len(imgPath)-1:
                    button_pressed = True
                    imgNumber += 1
                    print("RIGHT, imgNumber: ", imgNumber)
                    count = 0
                    annotations = [[]]
                    annotation_count = -1
                    annotation_start = False

                elif left_fingers == [1, 0, 0, 0, 0]: button_pressed = False
                    # else: button_pressed = False

        #finger_gesture_delay
                # if button_pressed == True:
                #     annotations = [[]]
                #     annotation_count = -1
                #     annotation_start = False
                #     if count > 15:
                #         button_pressed = False
                #         count = 0
                #     else:
                #         count += 1
                #         print(count)

    elif type == 1:
        button_pressed = False

    if type == 0:
        cv2.circle(imgCurrent_resized, indexFinger, 12, (0, 0, 255), cv2.FILLED)
    if type == 0 and left_fingers == [0, 1, 1, 0, 0]:
        if annotation_start == False:
            annotation_start = True
            annotation_count += 1
            print("new length of annotations: ", len(annotations))
            annotations.append([])
        
        print(annotation_count)
        annotations[annotation_count].append(indexFinger)
        # print(annotation_count)

         
         
    ###DELETE NOT WORKING
    # if type == 0 and left_fingers == [1, 0, 0, 0, 1] and button_pressed == False:
    #     # print("Erase")
    #     annotation_start = False
    #     button_pressed = True
    #     if annotations:
    #         # print(annotations)
    #         del annotations[-1]
    #         annotation_count -= 1
    #         print("after deletion, new length of annotations:", len(annotations))
    #         button_pressed = True

    for j in range (len(annotations)):
         for i in range (len(annotations[j])):
            if i>0:
                cv2.line(imgCurrent_resized, annotations[j][i-1], annotations[j][i], (0, 0, 200), 12)

    
    if button_pressed == True:
        if count > 15:
            button_pressed = False
            count = 0
            print(button_pressed)
        else:
            # print("False")
            count += 1
            print("count: ", count)

            
        # print(fingers)

        # cx, cy = hand['center']

        # if cy<=gesture_threshold:

        #     #gesture_1-left
        #     if fingers == [1, 0, 0, 0, 0]:
        #         print('left')

        #     #gesture_2-right
        #     if fingers == [1, 0, 0, 0, 1]:
        #         print('right')


    # h,w,_ = img.shape
    # print(h, w)
    # imgCurrent_resized = cv2.resize(imgCurrent, (width, height))
    imgCurrent_resized[0:s_height, width-s_width:width] = img_resized

    #adding webcam image on the presentation slide
    cv2.imshow("img", img)
    cv2.imshow("Presentation Slides", imgCurrent_resized)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

