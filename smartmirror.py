###imports for google calendar and authentication###
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

## Imports for datetime
import datetime
import dateutil.parser

### imports for weather###
import pyowm

###import for speech recognition
import speech_recognition as sr

### import for nltk (language processing)
import nltk
from nltk.corpus import wordnet as wn

### Other Imports
import math
import time
from tkinter import *

### Imports for OpenCV
import cv2
import logging as log
from time import sleep
import PIL.Image
import PIL.ImageTk

### Imports for Threading
import threading

####################################
# Face recognition
# Face Detection Training Data Credit-shantnu
#https://github.com/shantnu/FaceDetect/
####################################
def recognizeFace(data):
    #this code is responsible for detecting faces
    cascPath = "haarcascade_frontalface_default.xml"
    #this xml contains the data needed to train the cascade to detect faces
    faceCascade = cv2.CascadeClassifier(cascPath)
    log.basicConfig(filename='webcam.log',level=log.INFO)
    video_capture = cv2.VideoCapture(1)
    #instantiate a cascade object, and then start the video stream
    while True:
        if not video_capture.isOpened():
            print('Unable to load camera.')
            sleep(5)
            pass

        ret, frame = video_capture.read()
        #captures the frame
        frame=cv2.flip(frame,1)
        #flips the frmae
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        #this frame is used for the tkinter feed
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #this frame is used for facial detection
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        #face detection code
        if len(faces)!=0:
            data.showInterface=True
        else:
            data.showInterface=False
        #responsible for turning mirror on/off if 
        # faces are detected
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            data.facePosition=((x,y,w,h))
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #draws rectangle on CV2 frame
        #gets the face position for drawing the rectangle, and 
        # also updates data with it
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #quit code, not used except in special cases
        data.frame=cv2image
        #sends the latest frame to data, so that it can be used by tkinter
        #cv2.imshow('Video', frame)
            ### Turn this on to debug what the camera feed is seeing###

    video_capture.release()
    cv2.destroyAllWindows()
    #closes windows and releases capture at the end

####################################
# Returns the Time
####################################
def getDateTime():
    today = datetime.datetime.today()
    stringDay = returnWeekday(today)
    #creates a datetime object for today
    return (time.strftime("%x"), time.strftime("%I:%M %p"), stringDay)
    #returns a formatted strong of the time and date for use in the clock


def returnWeekday(datetime):
    weekdays={0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
    # takes a datetime object and returns a string of the weekday
    return weekdays[datetime.weekday()]
    #returns the corresponding weekday of a specified week index(0=monday, 6=sunday

####################################
# Weather Functions
####################################

def returnDayForecast(weather, tempscale="fahrenheit"):
    time = weather.get_reference_time('date')
    formattedday = (time.strftime("%a, %m/%d "))
    minTemp = str(weather.get_temperature(tempscale)['min']) + "F"
    maxTemp = str(weather.get_temperature(tempscale)['max']) + "F"
    mornTemp = str(weather.get_temperature(tempscale)['morn']) + "F"
    dayTemp = str(weather.get_temperature(tempscale)['day']) + "F"
    eveTemp = str(weather.get_temperature(tempscale)['eve']) + "F"
    nightTemp = str(weather.get_temperature(tempscale)['night']) + "F"
    status = weather.get_status()
    statusCode=weather.get_weather_code()
    forecast = {"day": formattedday, "minTemp": minTemp, "maxTemp": maxTemp, "mornTemp": mornTemp,
                "dayTemp": dayTemp, "eveTemp": eveTemp, "nightTemp": nightTemp, "status": status,"code":statusCode}
    return forecast
    #this function takes a weather object (pyowm) and then returns a 
    # dictionary containing relevant weather information

def getWeather(data,lat=40.44, lng=-79.94, tempscale="fahrenheit"):
    #this function gets the weather a specified location, with default valuse specified above
    owmkey = '7e5c480730efe5506204e7e1ae87ee12'
    owm = pyowm.OWM(owmkey)
    #this sets up the pyowm api key to call the api
    pathdict={2:"thunderstorm.png", 3:"raincloud.png",5:"raincloud.png",6:"rainsnow.png",8:"cloud.png",800:"sun.png",8000:"moon.png",80:"cloudynight.png",7:"mist.png"}
    #this dictionary is used for updating the icons
    observe = owm.weather_at_coords(lat, lng)
    weather = observe.get_weather()
    temperature = str(weather.get_temperature(tempscale)['temp']) + (" F")
    status = weather.get_status()
    code=weather.get_weather_code()
    d=datetime.timedelta(hours=5) #5 is used as a delta to account for timezones/UTC
    sunsetTime=weather.get_sunset_time('iso')
    sunriseTime=weather.get_sunrise_time('iso')
    # the .get methods return specific information about the weather
    formattedSunsetTime=dateutil.parser.parse(sunsetTime)-d
    formattedSunriseTime=dateutil.parser.parse(sunriseTime)-d
    #the dateutil parser allows for conversion of iso date strings into datetime objects, to be used later
    now = datetime.datetime.now().time()
    sunset = formattedSunsetTime.time()
    sunrise=formattedSunriseTime.time()
    #returns the time of the sunset after getting the datetime object
    if code==800:
        if now>sunset or now<sunrise:
            data.iconPath=pathdict[8000]
        else:
            data.iconPath=pathdict[800]
    else:
        if now>sunset or now<sunrise:
            if code//100==8:
                data.iconPath=pathdict[code//100*10]
            else:
                data.iconPath=pathdict[code//100]
        else:
            data.iconPath=pathdict[code//100]
    #this if/else determines which icon to use, and also takes into account whether its night time or not
    data.currentTemp = temperature
    data.weatherStatus=status
    data.weatherCode=code
    data.weatherStatus=status
    data.weatherRain=weather.get_rain()
    data.weatherWind=weather.get_wind()
    data.weatherHumidity=weather.get_humidity()
    #sets a up a number of weather related data elements with their correct value

def getForecast(lat=40.44, lng=-79.94, tempscale="fahrenheit"):
    #this function returns the 5 day forecast from pyowm 
    # (the longest forecast allowed by free api)
    owmkey = '7e5c480730efe5506204e7e1ae87ee12'
    owm = pyowm.OWM(owmkey)
    #sets the pyowm api up
    forecast = owm.daily_forecast_at_coords(lat, lng, limit=5)
    f = forecast.get_forecast()
    #calls the forecast, a list of weather obejcts
    weatherlist = []
    for weather in f:
        forecast = returnDayForecast(weather)
        weatherlist.append(forecast)
        #returns the formatted forecast for each day
    return weatherlist

####################################
# Speech Recognition
# reference
# https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
####################################

def recognizeSpeech():
    print("recognizing speech")
    speech = sr.Recognizer()
    #creatses an instance of the Recognizer
    with sr.Microphone() as source:
        #gets input from the microphone
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source)
        #adjusts for ambient noise and then starts the microphone input
    try:
        recognized = speech.recognize_google(audio)
        return recognized
        #attempts to recognize the audio using google
    except sr.UnknownValueError:
        print("couldnt recognize your audio")
    except sr.RequestError as e:
        print("couldnt get results from google; {0}".format(e))
        #exceptions are handled if the internet is
        # down, or if the audio is unrecognizable

    #this function makes a call to the google speech recognition engine, and then takes in the 
    # audio from your microphone and does the recognition on it

####################################
# Google authentication code taken from google
# https://developers.google.com/google-apps/calendar/quickstart/python
####################################
try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getCalEvents(date=None):
    #this function returns the calendar events, at the given date, or None if not specified
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    #gets google credentials
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    #gets the corrent time, and formats it
    print('Getting the upcoming events')
    calendaridList=[
        'g0tostl4q2q8dc3kblkqtuuv6g@group.calendar.google.com', #CMU Events
        '4dg6pu1jnusdpnkump4frglocs@group.calendar.google.com', #CMU HW
        '8jaema1ucgrt3g03fjuv8r5smk@group.calendar.google.com', #CMU Classes
        'euokutpi37i11v0h3igns7fjh4@group.calendar.google.com', #CMU
    ]
    #this list contains the calendar ID's that you want to get events from
    events=[]
    maxEvents=5
    for calendar in calendaridList:
        eventsResult = service.events().list(
            calendarId=calendar, timeMin=now, maxResults=maxEvents, singleEvents=True,
            orderBy='startTime').execute()
        events +=(eventsResult.get('items', []))
    #pulls the events from google calendar, up to maxEvents number of events per calendar

    if date==None:
        sortedMultiEvent=sorted(list(filter(lambda y : 'dateTime' in y['start'],events)),
                                key=lambda f: dateutil.parser.parse(f['start'].get('dateTime')))
    else:
        sortedMultiEvent=list(filter(lambda x: 'dateTime' in x['start'] and (dateutil.parser.parse(x['start']['dateTime']).date() == date),
                                     sorted(events,key=lambda f: dateutil.parser.parse(f['start'].get('dateTime')))))
        #these two one liners sort the multi event list into one that is
        # ordered by start time, and also checks to make sure they have a dateTime attribute so there are no crashes
    if not sortedMultiEvent:
        print('No upcoming events found.')
        return None
        #returns None if there are no events
    else:
        return sortedMultiEvent

####################################
# summary mode
####################################
#this code is relevant to drawing the main screen
def summaryMousePressed(event, data):
    pass

def summaryKeyPressed(canvas,event, data):
    if event.keysym == "space":
        data.listening=True
        data.noEvents=False
        t=threading.Thread(target=recognizeQuery,args=(data,))
        t.start()
    if event.keysym == "f":
        data.mode="easterEgg"
    #start voice recognition on space bar press
    #spawns recognition function in a new thread, so that the main tkinter window can continue to redraw

def summaryTimerFired(data):
    pass

def drawTime(canvas, data):
    date, time, weekday = getDateTime()
    paddingx=30
    paddingy = 100+249
    lineheight=80
    canvas.create_text(paddingx, paddingy-lineheight, text=time, font=(data.font, 60), fill="white",anchor="nw")
    canvas.create_text(paddingx, paddingy, text=weekday+", "+date, font=(data.font, 30), fill="white",anchor="nw")
    #draws the time module appropriately in the canvas, after pulling time from getDateTime()

def drawWeather(canvas, data):
    path="C:/Data/Brian/CMU Year 1/15-112/Term Project/weatherIcons/png/"+data.iconPath
    imag=PIL.Image.open(path)
    data.weatherIcon=PIL.ImageTk.PhotoImage(imag)
    height=imag.size[1]
    margin=30
    canvas.create_image(data.width-margin,margin,image=data.weatherIcon,anchor="ne")
    canvas.create_text(data.width-margin, margin+height+margin, text=data.currentTemp, font=(data.font, 30), fill="white",anchor="ne")
    canvas.create_text(data.width-margin, margin+height+70, text=data.weatherStatus, font=(data.font, 30), fill="white",anchor="ne")
    canvas.create_text(data.width - margin, margin + height + 70, text=data.weatherStatus, font=(data.font, 30),fill="white", anchor="ne")
    canvas.create_text(data.width - margin, margin + height + 120, text="Wind: " + str(data.weatherWind['speed'])+" MPH", font=(data.font, 20),
                       fill="white", anchor="ne")
    canvas.create_text(data.width - margin, margin + height + 150, text="Humidity: "+ str(data.weatherHumidity) + "%", font=(data.font, 20),
                       fill="white", anchor="ne")
    #draws the weather module onto the canvas

def buildSynSet(word):
    synset=set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synset.add(lemma.name())
    return synset
    #this function builds a set of synonyms for a
    # given word, using the nltk wordnet interface

def recognizeQuery(data):
    data.showForecast=False
    data.cantRecognize=False
    #sets up variables
    recognized=recognizeSpeech()
    #gets raw speech string
    processed = nltk.pos_tag(nltk.word_tokenize(recognized))
    #creates a list of each word in the phrase, split by word,
    # and tagged with the part of speech in context
    dicts = dict()
    #print(processed)
        ### Turn this on for debugging the speech recognition
    for i in processed:
        if i[1] in dicts:
            dicts[i[1]].add(i[0])
        else:
            dicts[i[1]]=set()
            dicts[i[1]].add(i[0])
    #builds a dictionary of sets of the parts of speech, to be referenced later

    if recognized=="mirror mirror on the wall who's the fairest of them all":
        data.mode="easterEgg"
        return
    #easter egg mode code
    try:
        if dicts["VB"].intersection(data.showSet)!=set() and dicts['NN'].intersection(data.weatherSet)!=set():
            print("showing weather")
            data.showForecast=True
            data.listening=False
        #NLP for showing the weather
        #takes the set of Verbs, and intersects it with the set of "show", and if non empty, continues checking.
        #likewise for the Noun

        elif dicts["VB"].intersection(data.setSet) !=set() and dicts['NN'].intersection(data.reminderSet) !=set():
            data.listening = False
            data.promptText = "What is the reminder?"
            data.canvas.create_text(data.width//2,data.height//2,text=data.promptText,font=(data.font,30),fill="white")
            addReminder(data)
            #does the same NLP for showing reminders, then draws in the query for prompting
            # what the reminder is, and calls the addReminder function

        elif dicts["VB"].intersection(data.showSet)!=set() and dicts["NN"].intersection(data.scheduleSet)!=set():
            data.listening=False
            months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                      "September": 9, "October": 10, "November": 11, "December": 12}
            #does the same NLP for showing the the schedule
            if dicts["NN"].intersection(data.todaySet):
                data.partialCalDay=datetime.datetime.now().date()
                data.partialEvents=getCalEvents(data.partialCalDay)
                if data.partialEvents!=None:
                    data.mode="partialCalDay"
                else:
                    data.noEvents=True
            #does NLP for identifying "Today"
            elif dicts["NN"].intersection(data.tomorrowSet):
                data.partialCalDay=datetime.datetime.now().date()
                delta = datetime.timedelta(days=1)
                data.partialEvents=getCalEvents(data.partialCalDay+delta)
                if data.partialEvents!=None:
                    data.mode="partialCalDay"
                else:
                    data.noEvents=True
            # does NLP for identifying "Tomorrow"
            elif "NNP" in dicts:
                if "Monday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="monday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                #Does NLP for identifying Monday (same for Tuesday, etc)
                #continues to add days to the current day, until weekday matches
                # specified day, and then calls partial Cal events on that day
                elif "Tuesday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="tuesday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                elif "Wednesday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="wednesday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                elif "Thursday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="thursday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                elif "Friday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="friday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                elif "Saturday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="saturday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta
                elif "Sunday" in dicts["NNP"]:
                    data.partialCalDay=datetime.datetime.now().date()
                    delta=datetime.timedelta(days=1)
                    for i in range(0,7):
                        if data.partialCalDay.strftime("%A").lower()=="sunday":
                            data.partialEvents=getCalEvents(data.partialCalDay)
                            if data.partialEvents!=None:
                                data.noEvents=False
                                data.mode="partialCalDay"
                            else:
                                data.noEvents=True
                        else:
                            data.partialCalDay+=delta

                elif min(dicts["NNP"]) in months:
                    day=int(min(dicts["CD"])[:-2])
                    print(day,type(day))
                    month=months[min(dicts["NNP"])]
                    print(month,type(month))
                    year=datetime.datetime.now().year
                    print(year,type(year))
                    data.partialCalDay=datetime.date(year,month,day)
                    data.partialEvents=getCalEvents(data.partialCalDay)
                    data.mode="partialCalDay"
                #does NLP for queries of the form "Show me the schedule for December 21st"
                return
            else:
                data.mode="fullCal"
                return
                #otherwise just return the full agenda

    except Exception as e:
        print(e)
        data.lastCommand=recognized
        data.listening=False
        data.cantRecognize=True
        return
        #returns an exception, typically for audio that cant be recognized

def disableForcast(data):
    data.showForecast=False
    #disables the Forecast

def addReminder(data):
    reminder=recognizeSpeech()
    data.reminders.append(reminder)
    data.promptText=None


def drawPrompt(canvas,data):
    canvas.create_text(data.width//2,data.height//2,text=data.promptText,font=(data.font,30),fill="white")
    #draws the specified prompt in the center of the screen

def drawCalendar(canvas, data):
    events=data.events
    x = 3*data.height//4-60
    #sets up the initial location of drawing the calendar
    for event in events[0:5]:
        x += 60
        #Increments by the line height
        start=dateutil.parser.parse(event['start']['dateTime'])
        end= dateutil.parser.parse(event['end']['dateTime'])
        #creates datetime objects out of the dateTime strings
        if start.date()!=end.date():
            eventTime=start.strftime("%A, %b %d %Y")+": "+start.strftime("%I:%M %p") + " to " + end.strftime("%A, %b %d %Y")+": "+end.strftime("%I:%M %p")
            canvas.create_text(30, x, text=str(event['summary']), font=(data.font, 14), fill="white",anchor="nw")
            canvas.create_text(30, x+20, text=eventTime, font=(data.font, 14), fill="white",anchor="nw")
        else:
            eventTime = start.strftime("%A, %b %d %Y") + ": " + start.strftime("%I:%M %p") + " - " + end.strftime("%I:%M %p")
            canvas.create_text(30, x, text=str(event['summary']), font=(data.font, 14), fill="white",anchor="nw")
            canvas.create_text(30, x + 20, text=eventTime, font=(data.font, 14), fill="white",anchor="nw")
    #draws the calendar, by iterating through the list of events

def drawReminders(canvas,data):
    reminders=data.reminders
    starty= 3*data.height//4
    #sets up initial location of drawing the reminders
    dy=starty
    canvas.create_text(data.width-30,starty,text="Reminders:",font=(data.font, 12), fill="white", anchor="ne")
    for reminder in range(len(reminders)):
        dy+=20
        canvas.create_text(data.width-30,dy, text=str(reminder+1)+") "+str(reminders[reminder]),
                           font=(data.font, 12), fill="white",anchor="ne")
    #draws all reminders in the reminder list

def drawClock(canvas,data):
    hour=data.hour
    minute=data.minute
    x0=(data.width//2-data.width//5)-data.width//3
    x1=(data.width//2+data.width//5)-data.width//3
    #sets up intial x values
    y0=0
    y1=data.width//2
    #sets up initial y values
    width=(x1-x0)
    height=(y1-y0)
    cx,cy=(x0+x1)//2,((y0+y1)//2)-data.height//15
    r=min(width,height)//3
    #gets center and radius of circle
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="",outline="white",width=3)

    hour+=minute/60
    hourAngle=math.pi/2-(2*math.pi)*(hour/12)
    hourR=r*0.5
    hourX=cx+hourR*math.cos(hourAngle)
    hourY=cy-hourR*math.sin(hourAngle)
    canvas.create_line(cx,cy,hourX,hourY,fill="white",width=2)
    #draws hour hand based on angle

    minuteAngle=math.pi/2-(2*math.pi)*(minute/60)
    minuteR=r*0.9
    minuteX=cx+minuteR*math.cos(minuteAngle)
    minuteY=cy-minuteR*math.sin(minuteAngle)
    canvas.create_line(cx,cy,minuteX,minuteY,fill="white",width=2)
    #draws minute hand based on angle

    #this code draws the clock at the correct location on the canvas

def drawForecast(canvas, data):
    forecasts = getForecast()
    margin = data.height//2-65
    shiftIncrement=120
    #sets up initial values for drawing the forecast
    shift=data.width//2-2*shiftIncrement
    for day in range(len(forecasts)):
        weather = forecasts[day]
        #gets forecast for each day
        code = weather['code']
        pathdict = {2: "thunderstorm.png", 3: "raincloud.png", 5: "raincloud.png", 6: "rainsnow.png", 8: "cloud.png",
                    800: "sun.png", 8000: "moon.png", 80: "cloudynight.png", 7: "mist.png"}

        if code == 800:
                iconPath = pathdict[800]
        else:
                iconPath = pathdict[code // 100]
        #decides what icon to use for each day

        path = "C:/Data/Brian/CMU Year 1/15-112/Term Project/weatherIcons/png/" + iconPath
        imag = PIL.Image.open(path)
        width = 50
        wpercent = (width / float(imag.size[0]))
        hfactor = int   ((float(imag.size[1])) * float(wpercent))
        imag = imag.resize((width, hfactor), PIL.Image.ANTIALIAS)
        #resizes icon, and then draws the icon

        data.forecastIcons.append(PIL.ImageTk.PhotoImage(imag))
        #appends to forecast Icon list

        canvas.create_image(0+shift, margin+45, image=data.forecastIcons[day])

        canvas.create_text(0+shift, margin, text=weather['day'], font=(data.font, 16), fill="white")
        canvas.create_text(0+shift, margin+90, text="High: "+weather['maxTemp'], font=(data.font, 14),
                           fill="white")
        canvas.create_text(0+shift, margin+110, text="Low: "+weather['minTemp'], font=(data.font, 14),
                           fill="white")
        canvas.create_text(0+shift, margin + 130, text=weather['status'], font=(data.font, 14),
                           fill="white")
        #creates the image, and the text for each forecast
        shift+=shiftIncrement

def centerDraw(canvas,data,text):
    canvas.create_text(data.width // 2, data.height // 2, text=text,
                       font=(data.font, 30),
                       fill="white")
    #draws text in the center of the screen

def drawListening(canvas,data):
    centerDraw(canvas,data,"Listening")
    #draws "Listening" in the center of the screen

def drawNoEvents(canvas,data):
    centerDraw(canvas,data,"No events found for that day")
    #draws "No events found"

def drawCantRecognize(canvas,data):
    centerDraw(canvas,data,"Can't recognize that voice command")
    canvas.create_text(data.width // 2, data.height // 2+40, text='"' + data.lastCommand + '"',
                       font=(data.font, 30),
                       fill="white")
    #draws "cant recognize voice command"

def summaryRedrawAll(canvas, data):
    drawTime(canvas, data)
    drawWeather(canvas, data)
    drawCalendar(canvas, data)
    drawClock(canvas,data)
    drawReminders(canvas,data)
    if data.promptText != None:
        drawPrompt(canvas,data)
    if data.showForecast==True:
        drawForecast(canvas,data)
    if data.listening==True:
        drawListening(canvas,data)
    if data.noEvents==True:
        drawNoEvents(canvas,data)
    if data.cantRecognize==True:
        drawCantRecognize(canvas,data)
    #draws summary mode, and any extra prompts depending on flags set.

####################################
# Full Calendar mode
####################################

def fullCalMousePressed(event, data):
    pass


def fullCalKeyPressed(event, data):
    if event.keysym=="BackSpace":
        data.mode="summary"
    #goes back to summary

def fullCalTimerFired(data):
    pass
def drawFullCalendar(canvas,data):
    events = data.events
    x = 30
    for event in events[0:20]:
        x += 60
        start = dateutil.parser.parse(event['start']['dateTime'])
        end = dateutil.parser.parse(event['end']['dateTime'])
        if start.date() != end.date():
            eventTime = start.strftime("%A, %b %d %Y") + ": " + start.strftime("%I:%M %p") + " to " + end.strftime(
                "%A, %b %d %Y") + ": " + end.strftime("%I:%M %p")
            canvas.create_text(data.width//2, x, text=str(event['summary']), font=(data.font, 16), fill="white",
                               anchor="center")
            canvas.create_text(data.width//2, x + 20, text=eventTime, font=(data.font, 16), fill="white",
                               anchor="center")
        else:
            eventTime = start.strftime("%A, %b %d %Y") + ": " + start.strftime("%I:%M %p") + " - " + end.strftime(
                "%I:%M %p")
            canvas.create_text(data.width//2, x, text=str(event['summary']), font=(data.font, 16), fill="white",
                               anchor="center")
            canvas.create_text(data.width//2, x + 20, text=eventTime, font=(data.font, 16), fill="white",
                               anchor="center")
    #draws the full calendar, taking in the data.events list
    #follows same structure as calendar module

def fullCalRedrawAll(canvas, data):
    drawFullCalendar(canvas,data)

####################################
#Partial Calendar Agenda mode
####################################

def partialCalDayMousePressed(event, data):
    pass

def partialCalDayKeyPressed(event, data):
    if event.keysym=="BackSpace":
        data.mode="summary"
    #goes back to summary

def partialCalDayTimerFired(data):
    pass

def drawPartialCalendar(canvas,data):
    events = data.partialEvents
    x = 30
    for event in events:
        x += 60
        start = dateutil.parser.parse(event['start']['dateTime'])
        end = dateutil.parser.parse(event['end']['dateTime'])
        if start.date() != end.date():
            eventTime = start.strftime("%A, %b %d %Y") + ": " + start.strftime("%I:%M %p") + " to " + end.strftime(
                "%A, %b %d %Y") + ": " + end.strftime("%I:%M %p")
            canvas.create_text(data.width // 2, x, text=str(event['summary']), font=(data.font, 16),
                               fill="white",
                               anchor="center")
            canvas.create_text(data.width // 2, x + 20, text=eventTime, font=(data.font, 16),
                               fill="white",
                               anchor="center")
        else:
            eventTime = start.strftime("%A, %b %d %Y") + ": " + start.strftime("%I:%M %p") + " - " + end.strftime(
                "%I:%M %p")
            canvas.create_text(data.width // 2, x, text=str(event['summary']), font=(data.font, 16),
                               fill="white",
                               anchor="center")
            canvas.create_text(data.width // 2, x + 20, text=eventTime, font=(data.font, 16),
                               fill="white",
                               anchor="center")
    #draws the partial calendar, based on specified date
    #follows same structure as getfullcalendar, but with only partial events list

def partialCalDayRedrawAll(canvas, data):
    drawPartialCalendar(canvas, data)

####################################
#Easter Egg Mode
####################################

def easterEggMousePressed(event, data):
    pass

def easterEggKeyPressed(event, data):
    if event.keysym=="BackSpace":
        data.mode="summary"

def easterEggTimerFired(data):
    pass

def drawVideo(canvas,data):
    x,y,w,h=data.facePosition
    #gets the position of the face
    img = PIL.Image.fromarray(data.frame)
    imgwidth=img.size[0]
    imgheight=img.size[1]
    tkImage = PIL.ImageTk.PhotoImage(img)
    cornerx=(data.width//2-imgwidth//2)
    cornery=(data.height//2-imgheight//2)
    data.displayImage=tkImage
    canvas.create_image(cornerx,cornery,image=data.displayImage, anchor="nw")
    #the "video feed" is displayed by constantly updating an image in the center of the canvas,
    #which is updated by the recognizeFaces function

    arrow1 = PIL.Image.open("arrowse.png")
    arrow2 = PIL.Image.open("arrowsw.png")
    arrow3 = PIL.Image.open("arrowne.png")
    arrow4 = PIL.Image.open("arrownw.png")
    data.arrow1 = PIL.ImageTk.PhotoImage(arrow1)
    data.arrow2 = PIL.ImageTk.PhotoImage(arrow2)
    data.arrow3 = PIL.ImageTk.PhotoImage(arrow3)
    data.arrow4 = PIL.ImageTk.PhotoImage(arrow4)
    #sets up images to be used for arrows

    canvas.create_image(cornerx+x,cornery+y,image=data.arrow1,anchor="se")
    canvas.create_image(cornerx + x+w, cornery + y, image=data.arrow2, anchor="sw")
    canvas.create_image(cornerx + x, cornery + y+h, image=data.arrow3, anchor="ne")
    canvas.create_image(cornerx + x+w, cornery + y+h, image=data.arrow4, anchor="nw")
    #draws arrows at corners of face

def easterEggRedrawAll(canvas, data):
    drawVideo(canvas,data)

def init(data):
    data.font = "Champagne & Limousines"
    data.showInterface=False
    data.canvas=None

    data.mode = "summary"
    data.events=getCalEvents()
    data.hour=datetime.datetime.now().time().hour%12
    data.minute=datetime.datetime.now().time().minute

    data.weatherIcon=None
    data.currentTemp=0
    data.weatherCode=0
    data.iconPath=""
    data.weatherStatus=""
    data.weatherRain = None
    data.weatherWind = None
    data.weatherHumidity = None

    data.promptText=None

    data.reminders=[]

    data.forecastIcons=[]

    data.showForecast=False

    data.speechRec=""

    data.listening=False

    data.partialEvents=None

    data.noEvents=False

    data.cantRecognize=False

    data.lastCommand=""
    data.frame=None
    data.displayImage=None
    data.facePosition=tuple()
    data.arrow1 = None
    data.arrow2 = None
    data.arrow3 = None
    data.arrow4 = None

    data.showSet = buildSynSet("show")
    data.weatherSet = buildSynSet("weather")
    data.setSet = buildSynSet("set")
    data.reminderSet = buildSynSet("reminder")
    data.scheduleSet = buildSynSet("schedule")
    data.todaySet = buildSynSet("today")
    data.tomorrowSet = buildSynSet("tomorrow")

####################################
# Mode Switcher
####################################

def mousePressed(event, data):
    if (data.mode == "fullCal"):
        fullCalMousePressed(event, data)
    elif (data.mode == "summary"):
        summaryMousePressed(event, data)
    elif (data.mode == "partialCalDay"):
        partialCalDayMousePressed(event,data)
    elif (data.mode == "easterEgg"):
        easterEggMousePressed(event,data)

def keyPressed(canvas,event, data):
    if (data.mode == "fullCal"):
        fullCalKeyPressed(event, data)
    elif (data.mode == "summary"):
        summaryKeyPressed(canvas,event, data)
    elif (data.mode == "partialCalDay"):
        partialCalDayKeyPressed(event,data)
    elif (data.mode == "easterEgg"):
        easterEggKeyPressed(event,data)

def timerFired(data):
    if (data.mode == "fullCal"):
        fullCalTimerFired(data)
    elif (data.mode == "summary"):
        summaryTimerFired(data)
    elif (data.mode == "partialCalDay"):
        partialCalDayTimerFired(data)
    elif (data.mode == "easterEgg"):
        easterEggTimerFired(data)


def redrawAll(canvas, data):
    if data.showInterface:
        if (data.mode == "fullCal"):
            fullCalRedrawAll(canvas, data)
        elif (data.mode == "summary"):
            summaryRedrawAll(canvas, data)
        elif (data.mode == "partialCalDay"):
            partialCalDayRedrawAll(canvas,data)
        elif (data.mode == "easterEgg"):
            easterEggRedrawAll(canvas,data)

####################################
# Run Function taken from 112 website
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='black', width=0,outline="black")
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(canvas,event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Set up data and call init
    class Struct(object): pass

    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 34  # milliseconds

    init(data)
    # create the root and the canvas

    opencv = threading.Thread(target=recognizeFace, args=(data,))
    opencv.daemon=True
    opencv.start()
    #spawns a new thread for recognizeFace, so that openCV doesn't block tkinter

    getWeather(data)
    root = Tk()
    root.overrideredirect(True)
    root.geometry('%dx%d+%d+%d'% (900,1440,1920,0))
    #this code runs the tkinter window without a border,
    # and also in a specified location when it starts
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()

    data.canvas = canvas

    # set up events
    root.bind("<Button-1>", lambda event:
    mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
    keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye! #112")


run(900,1440)

###ICONS CREDIT: ###
### Weather Collection by Andrejs Kirma from the Noun Project###
###mist by sameleh from the Noun Project###
