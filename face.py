import cv2
import numpy as np
import face_recognition as fr
import pickle
import time
from voice_recognition import *
from pyttsx3 import speak
from database import *
from datetime import datetime
import pyrebase


data = Database()
config = {
    "apiKey": "AIzaSyCEmnNdv_vjt4IKtsCfUJud18TN3YpCKVA",
    "authDomain": "cvip-a44cd.firebaseapp.com",
    "databaseURL": "https://cvip-a44cd.firebaseio.com",
    "projectId": "cvip-a44cd",
    "storageBucket": "cvip-a44cd.appspot.com",
    "messagingSenderId": "286686795913",
    "appId": "1:286686795913:web:482dbcd478c29eea790e58",
    "measurementId": "G-8PLRVPBBF7"
}

def savetoCloud_mainface(ubid):
    path_on_cloud = "main_faces/"+str(ubid)+".jpg"
    path_local = "data/faces/main_faces/"+str(ubid)+".jpg"
    print("Saving to Cloud....")
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    storage.child(path_on_cloud).put(path_local)

def savetoCloud_timeface(txt):
    path_on_cloud = "time_faces/"+str(txt)+".jpg"
    path_local = "data/faces/time_faces/"+str(txt)+".jpg"
    print("Saving to Cloud....")
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    storage.child(path_on_cloud).put(path_local)

def save_newface(img,ubid):
    '''
    Save the New Person face image to the database
    '''
    ubid = str(ubid)
    ubid = ubid.replace(" ","")
    txt = 'data/faces/main_faces/'+ubid +'.jpg'
    cv2.imwrite(txt,img)
    savetoCloud_mainface(ubid)

def save_timeface(ubid,inout):
    '''
    Save the Current face image with Time Stamp
    '''
    ubid = str(ubid)
    ubid = ubid.replace(" ","")
    now = datetime.now()
    time = now.strftime("%B_%d_%A_%Y_%H-%M-%S")
    r = outcom()
    img = r[1]
    loc = r[0]
    cloud = ''
    # img = get_roi(img,loc[0])
    if(inout=='in'):
        txt = 'data/faces/time_faces/'+ubid+'_'+time +'_IN.jpg'
        cloud = ubid+'_'+time +'_IN'
        
    else:
        txt = 'data/faces/time_faces/'+ubid+'_'+time +'_OUT.jpg'
        cloud = ubid+'_'+time +'_OUT'
    cv2.imwrite(txt, img)
    savetoCloud_timeface(cloud)

def get_roi(image, location):
    '''
    Get Region of Interest by input of rectangle coords
    '''
    top = location[0] 
    right = location[1] 
    bottom = location[2] 
    left = location[3] 
    
    width = abs(right - left)
    height = abs(bottom - top)
    x = abs(right - width)
    y = abs(bottom - height)
    roi = image[y-20:y+height+20, x-20:x+width+20]
    print('Capturing the Current Person Face')
    return roi

def draw_box_name(Bigframe,scale,name,location):
    '''
    Function to Draw bounding boxes and name of the faces found.
    '''
    top = location[0] 
    right = location[1] 
    bottom = location[2] 
    left = location[3] 
    top = int((1/scale)*top)
    right = int((1/scale)*right)
    bottom = int((1/scale)*bottom)
    left = int((1/scale)*left)
    # Draw a box around the face
    cv2.rectangle(Bigframe, (left, top), (right, bottom), (0, 0, 255), 2)
    # Draw a label with a name below the face
    cv2.rectangle(Bigframe, (left, bottom + 10), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(Bigframe, name, (left + 6, bottom +8), font, 0.5, (255, 255, 255), 1)
    return Bigframe

def response_window(face_locations,result,Bigframe,known_face_names,face_encoding):
    '''
    This the main Response Tree with multiple if cases which handles the User Inputs.
    '''
    if(len(face_locations)>0):
        #ENTER THE RESPONSE TREE
        ubid = ''
        uniqueID = ''
        update_flag(False)
        known_face_names, known_face_encodings, uniqueID_list, ubid_list = [],[],[],[]
        feature_lists = data.getNameAndFeatureVector()
        if feature_lists != None :
            known_face_names, known_face_encodings, uniqueID_list, ubid_list = feature_lists
        if(result[4]==False):
            totext('An Unknown Face Found, Would you like to Register ?')
            response = voice_input() #get user input
            if(response=="yes"):
                totext('Do you have an UB ID ?')
                response_ubid = voice_input()
                if(response_ubid=="yes"):
                    totext('Please Tell your UBID')
                    ubid = voice_input() #Get user UBID input
                    ubid = str(ubid)
                    ubid = ubid.replace(" ","")
                    check_name = data.getUbidStatus(ubid)
                    #UBID CHECK FUNCTION
                    if(check_name != None):
                        totext('Capturig your Image')
                        totext('Make sure only Your Face is Seen')
                        time.sleep(5)
                        r = outcom()
                        img = r[1]
                        loc = r[0]
                        #Save the new face pic with encoding to DB
                        current_face = get_roi(img,loc[0])
                        current_encoding = r[3]
                        new_face = current_face
                        new_encoding = current_encoding
                        new_name = check_name
                        d1 = {"name": new_name, "ubid":ubid,"faceEncoding":list(new_encoding)}
                        uniqueID =  data.postData(d1)
                        update_flag(True)
                        save_newface(new_face, ubid)

                        totext('New Entry successfull,would you like to continue '+new_name+'?')
                        response = voice_input() #get user input
                        if(response=="yes"):
                            #Check weather the person has already clocked it
                            clockin = data.checkClockedStatus(uniqueID)
                            if(clockin==False):
                                totext('Would you like to clockin now ?')
                                response_clkin = voice_input() #get user input
                                if(response_clkin=='yes'):
                                    #clockin the person wiht index result[1]
                                    clockin_data = data.clockInUser(uniqueID)
                                    totext('You have successfully clocked in')
                                    save_timeface(ubid,'in')
                                    time.sleep(5)
                                else:
                                    totext('Thankyou for using the service')
                                    time.sleep(5)
                            else:
                                totext('Would you like to clock Out ?')
                                response_clkout = voice_input() #get user input
                                if(response_clkout=='yes'):
                                    #clockin the person wiht index result[1]
                                    clockout_data = data.clockOutUser(uniqueID)
                                    totext('You have successfully clocked Out')
                                    save_timeface(ubid,'out')
                                    time.sleep(5)
                                else:
                                    totext('Thankyou for using the service')
                                    time.sleep(5)                   
                    else:
                        totext('Your UB ID does not match with our Records.')
                else:
                    totext('You cannot register without UB ID')
                    time.sleep(5)
            else:
                totext('Thankyou, you cannot be clocked in at the moment')
                time.sleep(5)
        if(result[4]==True):
            match_index = result[5]
            text = 'Person found is ['+known_face_names[match_index]+']'
            totext(text)
            totext('Are you '+known_face_names[match_index]+'?')
            name = known_face_names[match_index]
            ubid = ubid_list[match_index]  #Get UB ID
            uniqueID = uniqueID_list[match_index] # Get Unique ID
            response = voice_input() #get user input
            if(response=="yes"):
                #Check weather the person has already clocked it
                clockin = data.checkClockedStatus(uniqueID)
                if(clockin==False):
                    totext('Would you like to clock in now ?')
                    response_clkin = voice_input() #get user input
                    if(response_clkin=='yes'):
                        #clockin the person wiht index result[1]
                        clockin_data = data.clockInUser(uniqueID)
                        save_timeface(ubid,'in')
                        totext('You have successfully clocked in')
                        time.sleep(5)
                    else:
                        totext('Thankyou for using the service')
                        time.sleep(5)
                else:
                    totext('Would you like to clock Out ?')
                    response_clkout = voice_input() #get user input
                    if(response_clkout=='yes'):
                        #clockin the person wiht index result[1]
                        clockout_data = data.clockOutUser(uniqueID)
                        save_timeface(ubid,'out')
                        totext('You have successfully clocked Out')
                        time.sleep(5)
                    else:
                        totext('Thankyou for using the service')
                        time.sleep(5)
            else:
                time.sleep(3)

def tocom(l):
    #Function to write the output of the Face recognition to com.data
    with open('com.data', 'wb') as filehandle:
        pickle.dump(l, filehandle)

def outcom():
    #Function to retrive output from com.data
    with open('com.data', 'rb') as filehandle:
        outlist = pickle.load(filehandle)
    return outlist

def totext(l):
    #Function to write and speak the output of the Response to display
    speak(l)

    print(l)

    with open('text.data', 'wb') as filehandle:
        pickle.dump(l, filehandle)
        
def outtext():
    #Function to write the output of the Response to display
    with open('text.data', 'rb') as filehandle:
        outlist = pickle.load(filehandle)
    return outlist

def update_flag(flag):
    with open('update.data', 'wb') as filehandle:
        pickle.dump(flag, filehandle)

def update_check():
    with open('update.data', 'rb') as filehandle:
        outlist = pickle.load(filehandle)
    return outlist

