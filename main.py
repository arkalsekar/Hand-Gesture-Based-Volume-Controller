import cv2
import mediapipe as mp
import time
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np 
import math

# Min Hand Distance , Max hand distance 15 , 55
# minimum vol , maximum = -65, 0 

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
print(volRange)
minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 80
# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)
    image_hight, image_width, _ = image.shape
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    imgL = results.multi_hand_landmarks
    # if imgL is not None:
    #   for il in imgL:
    #         print(il.landmarks)
    # # print(imgL)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:            
            # print(hand_landmarks.landmark)
            # print(

            #   f'Index finger tip coordinate: (',
            #   f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
            #   f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_hight})'
            # )

            # mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            indexX, indexY = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width, hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_hight
            ThX, ThY = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * image_width, hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * image_hight
            ThCor = int(ThX), int(ThY)
            # print(indexX, indexY)
            indexCor = int(indexX), int(indexY)
            # print(indexCor)
            cv2.circle(image, tuple(indexCor), 20, (0, 0, 256), -1)
            # print(ThCor, indexCor)
            
            length = math.hypot(ThX - indexX, ThY - indexY)
            # print(length)

            vol = np.interp(length, [15, 155], [minVol, maxVol]) 
            volBar = np.interp(length, [3, 155], [380, 80]) 
            # print(vol)
            # if pyautogui.press('s'):
            #       time.sleep(3)

            # else:    
            a = volume.SetMasterVolumeLevel(vol, None)
              # print(a)

            if indexCor is not None:
                  cv2.line(image, indexCor, ThCor, (256, 0, 0), 2)


            cv2.circle(image, tuple(ThCor), 20, (0, 0, 256), -1)
    
    
    cv2.rectangle(image, (60, 380), (80, 80), (0, 256, 0), 2)
    cv2.rectangle(image, (60, int(380)), (80, int(volBar)), (0, 256, 0), -1)
    
    
    cv2.putText(image, "Volume Controller", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (256, 0, 0), 2)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
