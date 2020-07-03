from firebase import firebase  
from datetime import date
from datetime import datetime
import numpy as np
import cv2
import imghdr
import base64
import json


'''
Stucture of Our Main Object
Note that a unique id will be created when we save it for the first time in db, its not show currently.
We will use this id for all transcations

object = {
"userName":'',
"ubid":'',
"faceEncoding":[]
"dayAndTime":[{
                'day':'',
                'startTime':'',
                'endTime':''}]
}

'''

today = date.today()
date1= today.strftime("%d/%m/%Y")
        
now = datetime.now()
start_time = now.strftime("%H:%M:%S")
        

class Database:
    def __init__(self):
        self.firebase = firebase.FirebaseApplication('https://cvip-a44cd.firebaseio.com/', None)
        
    '''
    To save the first data object
    Pass it to a dictionary consisting of following parameters:name,ubid,feature vector
    Structure of the dictionary eg -   {"name":'Gerald',"ubid":5033999,"faceEncoding":[1,2,3,4,5]}
    It will automatically insert date and start time in the main object
    '''
    
    def postData(self,d):
        data={ "userName":d['name'],
               "dayAndTime":[{ "day": date1,
               "startTime":"",
               "endTime":" "
                    }],
               "ubid":d['ubid'],
               "faceEncoding":d['faceEncoding']}
        
        print("Posting data in DB")
        
        result = self.firebase.post('/timeclock/',data)  
        
        uid = dict(result)
        
        return uid['name']
        
        
        
    #This method will retrieve all the data from database  
    '''
    Sample of a single object returned from database
    
    obj = {'-M5VP8cUF8UehCDc8fV4': 
                               {'dayAndTime': [{
                                               'day': '22/04/2020', 
                                               'endTime': ' ', 
                                               'startTime': '01:42:21'}], 
                                'faceEncoding': [1, 2, 3, 4, 5], 
                                'ubid': 5033, '
                                userName': 'Gerald'}}
    
    '''
    def getData(self):
        result = self.firebase.get('/timeclock/', '')
        print(result)
        return result
        
      #Pass the Unique Key to Get That Particular Data  
    def getSingleData(self,key):
        result = self.firebase.get('/timeclock/', key)  
        #print(result)  
        return result
    
    #To update a single object, pass it the unique key and updated data object
    def updateSingleData(self,id,data):
        rs=self.firebase.patch('/timeclock/'+id, data)
        print('updated')  
        
        
    def clockInUser(self,id):
        data = self.getSingleData(id)
        x = data['dayAndTime']

        for dict1 in x:
            if (dict1['day'] == date1):
                dict1['startTime'] = start_time

        data['dayAndTime'] = x
        rs = self.firebase.patch('/timeclock/' + id, data)

        return data
        
        
    def clockOutUser(self,id):
        data=self.getSingleData(id)
        x=data['dayAndTime']
        
        for dict1 in x:
            if(dict1['day'] == date1):
                dict1['endTime']=start_time
        
        data['dayAndTime']=x
        rs=self.firebase.patch('/timeclock/'+id, data)
        
        return data
        
        #check if user is clocked in or out
        
    def checkClockedStatus(self,id):
        data=self.getSingleData(id)
        x=data['dayAndTime']
        status = True
        
        
        for dict1 in x:
            if(dict1['day'] == date1):
                if(dict1['startTime'] == ''):
                    status=False
        
        return status
        
        
        
    def getNameAndFeatureVector(self):
        res = self.firebase.get('/timeclock/', '')
        if(res != None):
            name=[]
            featureVector=[]
            uid=[]
            ubid=[]
            for obj1 in res:
                uid.append(obj1)
                obj2=res[str(obj1)]
                name.append(obj2['userName'])
                featureVector.append(np.array(obj2['faceEncoding']))
                ubid.append(obj2['ubid'])
            return name,featureVector,uid,ubid
        else:
            return [],[],[],[]
    
    
    def dayAndDateValues(self):
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%Y")
        
        hours = now.strftime("%H")
        seconds = now.strftime("%S")
        minutes = now.strftime("%M")
        
        return day,month,year,hours,seconds,minutes
    
    def getUbidStatus(self,ubid):
        data = self.firebase.get('/ubidDb/', None)
        out = None
        ubid = str(ubid)
        ubid = ubid.replace(" ","")
        for dict1 in data:
            x=(data[dict1])
            if(str(ubid) == x['ubid']):
                out =  x['name']
                break

        return  out
        

'''

a=Database()
d1={"name":'Gautam',"ubid":5033,"faceEncoding":[1,2,3,4,5]}

#a.updateSingleData(a.getSingleData())
c=a.getData()
f=list(c.keys())
print(f)
res=a.getSingleData(f[0])
#print(res)

#res['userName'] = 'gautam'
res['dayAndTime'].append({'day':'24/04/2019'})

#print(res)
#a.updateSingleData(str(f[0]),res)


img=cv2.imread('3.png')
imgType= imghdr.what('3.png')
print(imgType)
img_str = cv2.imencode('.png',img)[1].tostring()
print(type(img_str))



a=Database()
d1={"name":'Gautam111',"ubid":5033,"faceEncoding":[1,2,3,4,5]}
img=cv2.imread('3.png') 

with open("3.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

a.postData(d1, encoded_string)
 
#cv2.imwrite('F:/CV/Final/data/3.png', img)
''' 
#
# a = Database()

# a.getUbidStatus("1111")

# firebase = firebase.FirebaseApplication('https://cvip-a44cd.firebaseio.com/', None)
# result = firebase.get('/ubidDb', None)
# for dict1 in result:
#             x=(result[dict1])
#             print(x['ubid'])

# a.clockInUser('-M5tqBEF89MM-FIi1XBl')
# print(a.checkClockedStatus('-M5tqBEF89MM-FIi1XBl'))
# # known_face_names, known_face_encodings, uniqueID, ubid = a.getNameAndFeatureVector()
# # print(known_face_names)
# known_face_names, known_face_encodings, uniqueID, ubid = a.getNameAndFeatureVector()
# print(ubid)
