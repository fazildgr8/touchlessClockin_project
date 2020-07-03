from face import *
import cv2
import numpy as np
from imutils.video import VideoStream
from imutils import resize
import time
import face_recognition as fr
from datetime import datetime
from  database import *

'''
This the program which takes the 
video feed and applies dnn to detect and recognize faces
'''

scale = 1 # Scale factor for the frames at which face recognition is applied
res = (640 , 480)
# Start the Video Feed
vs = VideoStream(src=0,resolution=res).start() # Define the Video Source (Webcam)
time.sleep(0.2) # Warm up the webcam

logo = cv2.imread('data/UB_logo.png')
logo = resize(logo, width=150)
'''
Load the Known Faces encoding and their corresponding names
'''
totext('')
# with open('encodings.data', 'rb') as filehandle:
#     # read the data as binary data stream
#     known_face_encodings = pickle.load(filehandle)
# with open('names.data', 'rb') as filehandle:
#     # read the data as binary data stream
#     known_face_names = pickle.load(filehandle)


data = Database()
known_face_names, known_face_encodings, uniqueID_list, ubid_list = [], [], [], []
feature_lists = data.getNameAndFeatureVector()

if feature_lists != None:
    print('Updating Known Face and Encoding Lists.')
    known_face_names, known_face_encodings, uniqueID_list, ubid_list = feature_lists
    update_flag(False)

'''
The Main Loop STARTS here
'''
while(True):
    Bigframe = vs.read() # Start Reading the frames from Video Feed
    frame = cv2.resize(Bigframe, (0, 0), fx=scale, fy=scale) # Frame where Image Processing is done
    rgb_frame = frame[:, :, ::-1] # Convert BGR to RGB
    draw = np.array([])
    # Time Stamp the Image
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_day = now.strftime("%A %d. %B %Y")

    # Draw the title and Logo to the Video Output
    cv2.putText(Bigframe, 'Touchless Clock IN System', (40, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
    Bigframe[0:logo.shape[0],480:logo.shape[1]+480] = logo
    cv2.putText(Bigframe, current_time, (530, 460), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(Bigframe, current_day, (490, 440), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1)


    '''
    SEARCH FOR Faces in the frame
    '''

    face_locations = fr.face_locations(rgb_frame) # Get list of Face Locations
    face_encodings = fr.face_encodings(rgb_frame, face_locations) # List of Face encodings


    # Loop the found face locations and encodings throught the Known Faces
    result = []
    if len(face_locations) < 1:
        tocom([None])
    else:
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = fr.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            # the known face with the smallest distance to the new face

            face_distances = fr.face_distance(known_face_encodings, face_encoding)

            if face_distances.any():
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
            else:
                best_match_index = 0
            location = [top, right, bottom, left]
            # print('Face Found - ['+name+']')

            if name == "Unknown":
                result = [face_locations, Bigframe, known_face_names, face_encoding, False, location] # If the found face is Unknow
                # Write the result data to communication data file
                tocom(result) 
            else:
                result = [face_locations, Bigframe, known_face_names, face_encoding, True, best_match_index, location] # If the found face is Known
                # Write the result data to communication data file
                tocom(result)
            # Draw the labels and Bounding Boxes to our captured frame
            Bigframe = draw_box_name(Bigframe,scale,name,location)


    text = outtext()
    cv2.putText(Bigframe, text, (0,450), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow('frame', Bigframe)
    if update_check()==True:
        print('Updating Known Face and Encoding Lists.')
        known_face_names, known_face_encodings, uniqueID, ubid = data.getNameAndFeatureVector()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tocom([None])
vs.stop()
cv2.destroyAllWindows()

'''
Reffered Library Src -  https://github.com/ageitgey/face_recognition
'''