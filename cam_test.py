#5

'''
USAGE:
python cam_test.py 
'''

import torch
import joblib
import torch.nn as nn
import numpy as np
import cv2
import argparse
import torch.nn.functional as F
import time
import cnn_models
import pyttsx3
import matplotlib.pyplot as plt
 
from torchvision import models

# load label binarizer
lb = joblib.load('outputs/lb.pkl')
#device=('cuda:0' if torch.cuda.is_available() else 'cpu')          
model = cnn_models.CustomCNN()            #change .to(device)
model.load_state_dict(torch.load('outputs/model.pth'))
print(model)
print('Model loaded')

def hand_area(img):
    hand = img[100:324, 100:324]
    hand = cv2.resize(hand, (224,224))
    return hand

cap = cv2.VideoCapture(0)

if (cap.isOpened() == False):
    print('Error while trying to open camera. Plese check again...')

# get the frame width and height
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# define codec and create VideoWriter object
out = cv2.VideoWriter('outputs/asl.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (frame_width,frame_height))

frame_rate = 0.7        
prev=0                  
finalText=""            

# read until end of video
while(cap.isOpened()):
    # capture each frame of the video
    time_elapsed=time.time() - prev     
    ret, frame = cap.read()
    # get the hand area on the video capture screen
    cv2.rectangle(frame, (100, 100), (324, 324), (20,34,255), 2)
    hand = hand_area(frame)

    image = hand
    
    image = np.transpose(image, (2, 0, 1)).astype(np.float32)
    image = torch.tensor(image, dtype=torch.float)               
    image = image.unsqueeze(0)
    
    outputs = model(image)
    _, preds = torch.max(outputs.data, 1)
    #print('PREDS', preds)
    #print(f"Predicted output: {lb.classes_[preds]}")

    
    cv2.putText(frame, lb.classes_[preds], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    if time_elapsed > 1./frame_rate:
     if cv2.waitKey(10) & 0xFF == ord(' '):
       prev = time.time() 
       mytext= lb.classes_[preds]
       if(mytext!="nothing"):
           if(mytext=="space"):
               finalText+=" "
           elif(mytext=="del"):
               finalText = finalText[:len(finalText) -1]
           else:
              finalText+=mytext
           print(finalText)
    

    
    cv2.putText(frame, finalText, (120, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.imshow('image', frame)
    out.write(frame)

    time.sleep(0.09)

    # press `q` to exit
    if cv2.waitKey(27) & 0xFF == ord('q'):             
        engine = pyttsx3.init()     
        engine.say(finalText)       
        engine.runAndWait()           
        break

# release VideoCapture()
cap.release()

# close all frames and video windows
cv2.destroyAllWindows()