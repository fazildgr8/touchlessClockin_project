#!/usr/bin/env python3


import speech_recognition as sr

def voice_input():

	# obtain audio from the microphone
	r = sr.Recognizer()
	out = ""
	with sr.Microphone() as source:
	    print("Say something!")
	    audio = r.listen(source)
	try:
	    # for testing purposes, we're just using the default API key
	    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
	    # instead of `r.recognize_google(audio)`
	    out = r.recognize_google(audio, language="en-IN")
	    print("You said [" + out +"]")
	except sr.UnknownValueError:
	    print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
	    print("Could not request results from Google Speech Recognition service; {0}".format(e))
	return out

