import cv2
import numpy
import time
from face import *

'''
This program reads the results from face recognitions 
and opens control to User Interaction functions
'''

out = [None]
tocom(out)
while(True):
	# Read the result file every 1 second buffer
	time.sleep(1)
	out = outcom()
	result = out
	if(result[0] != None):
		face_locations = result[0]
		Bigframe = result[1]
		known_face_names = result[2]
		face_encoding = result[3]
		print(result[4])
		response_window(face_locations,result,Bigframe,known_face_names,face_encoding)
	else:
		print(result[0])
		totext('')

	out = []
