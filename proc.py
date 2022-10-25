import numpy as np
import cv2
import pytesseract
from PyDictionary import PyDictionary
import Marker
import re


dictionary = PyDictionary()


def imgin(frame):
    resize_w = 640
    resize_h = 480
    if(frame.shape[0] > frame.shape[1]):
        resize_w = 480
        resize_h = 640
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Width and height of the box drawn
    w = 150
    h = 60
    string = ""

    # Objects
    marker = Marker.Marker()

    # Capture image frame
    frame = cv2.resize(frame, (resize_w,resize_h))

    # Identify maker position from the image
    cX, cY = marker.colour(frame, [0,5], displayMask=False)
    if cX != -1:
        # Draw white dot at the center of the marker
        cv2.circle(frame, (cX, cY), 2, (255, 255, 255, -1))

        startPoint = (int(cX-w/2), cY-h)
        endPoint = (int(cX+w/2), cY)
        cv2.rectangle(frame, startPoint, endPoint, (0,255,0), 1)
        # Crop image around area of interest
        cropFrame = frame[startPoint[1]:endPoint[1], startPoint[0]:endPoint[0]]
        if cropFrame.any():
            # Detect words in the cropped image
            contours = Detect_Text_Blob(cropFrame)
            # Find nearest word to the marker
            minX, minY, minW, minH = Nearest_Contour(cropFrame, contours, cX, cY)
            # Bound the nearest word in a red rectangle
            cv2.rectangle(cropFrame, (minX, minY), (minX+minW, minY+minH), (0, 0, 255), 1)
            # Identify text from the red rectangle, ideally it should be only one word
            translateFrame = cropFrame[minY:minY+minH, minX:minX+minW]
            text = pytesseract.image_to_string(translateFrame)
            # Replacing every character except english alphabets with space
            word = re.sub(r'[^A-Za-z+]', '', text)

            if word != '':
                string = Extract_Information(word)
            else:
                string = "<b>No Valid Word Detected.. Please Try Again.</b>"
        else:
            string = "<b>No Valid Word Detected.. Please Try Again.</b>"
    else:
        string = "<b>No Valid Word Detected.. Please Try Again.</b>"

    # Display image
    #cv2.imshow('frame', frame)
    cv2.imwrite("testhello.jpeg",frame)
    return(string)
    #cv2.imshow('cropFrame', cropFrame)
    #cv2.imshow('translateFrame', translate


def Detect_Text_Blob(image):
    # Change color image into grayscale image
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply binary threshold
    imgBinary = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 12)
    cv2.imwrite('Binary.jpeg', imgBinary)

    # Apply erosion to the image
    erosionKernel = np.ones((3,3), np.uint8)
    imgEroded = cv2.erode(imgBinary, erosionKernel, iterations=3)
    cv2.imwrite('Eroded.jpeg', imgEroded)

    # Detect countours in the image
    contours, hierarchy = cv2.findContours(imgEroded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(image, contours, -1, (0,255,0), 1)
    #cv2.imshow('text', image)

    return contours

def Nearest_Contour(image, contours, markerX, markerY):
    minDistance = np.inf
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 1)
        dist = np.sqrt((markerX-x)**2 + (markerY-y)**2)
        #print(str(markerX) + " " + str(x) + " " + str(dist),end= ' ')
        #print(str(markerY) + " " + str(y) + " " + str(dist))
        if dist < minDistance and w >= 50:
            minDistance = dist
            minX, minY, minW, minH = x, y, w, h

    if minDistance == np.inf:
        minX, minY, minW, minH = markerX, markerY, 2, 2

    return minX, minY, minW, minH

def Extract_Information(word):
    ans = ""
    ans += "<b>Word</b> : " + word + ".<br></br>"
    ans += "<b>Meanings</b> : <br></br>"
    meaning = dictionary.meaning(word)
    if meaning != None:
        for key in meaning.keys():
            ans += "<b>" + key + "</b> : "
            for i in range(len(meaning[key]) if len(meaning[key]) <= 5 else 5):
                ans += str(i+1) + ". " + meaning[key][i] + ".<br></br>"
        ans += ("<b>Synonyms</b> : " + ', '.join(dictionary.synonym(word)) + ".<br></br>").replace("_"," ")
        ans += ("<b>Antonyms</b> : " + ', '.join(dictionary.antonym(word)) + ".").replace("_"," ")
    else:
        ans += "<b>The word has no valid meaning. Please try again.</b>"

    return ans
