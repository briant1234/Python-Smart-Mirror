import string
import speech_recognition as sr
#import nltk
#nltk.download()
'''
r=sr.Recognizer()

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source) # adjusting for ambient noise

    print("say something")
    audio=r.listen(source)

#stop=r.listen_in_background(m,callback) # theoretically would start a background listener
try:
    print("Google thinks you said: "+r.recognize_google(audio))
except sr.UnknownValueError:
    print("couldnt recognize your audio")
except sr.RequestError as e:
    print("couldnt get results from google; {0}".format(e))

if r.recognize_google(audio)=="hello":
    print("HI BRIAN")

elif r.recognize_google(audio)=="show me the time":
    #return time
    pass

'''
import speech_recognition as sr
def recognizeSpeech():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)

        audio=r.listen(source)
    try:
        recognized=r.recognize_google(audio)
    except sr.UnknownValueError:
        print("couldnt recognize your audio")
    except sr.RequestError as e:
        print("couldnt get results from google; {0}".format(e))
    if recognized=="show weather":
        print("change mode to weather")

recognizeSpeech()
