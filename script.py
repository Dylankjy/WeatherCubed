# Operating System Lib
import core.api
import os

# AIY Libs
import aiy.cloudspeech
import aiy.audio
import aiy.voicehat


# Other libs
import pyowm              # OpenWeatherMap
import time               # Time Lib
from apscheduler.schedulers.blocking import BlockingScheduler #  Advanced Python Scheduler
from random import randint# Random Number
from pygame import mixer  # Music Lib
from threading import Thread

# Global Variables
status = None 
statusCode = 0 # For detection of rain.
temp = None
rainAlert = False # To prevent repeat rain alerts if weather has not changed.
hourPassAlert = False # To prevent repeat hour pass alerts.

# Music Global Variables
happy = ["chunky.mp3", "i_want_it_that_way.mp3", "kill_the_lights.mp3", "locked_out_of_heaven.mp3"]
moody = ["happy_now.mp3", "2002.mp3", "i_like_me_better.mp3", "lost_in_japan.mp3", "on_my_side.mp3", "paris_in_the_rain.mp3", "psycho.mp3"]
rain = ["alcyone.mp3", "idontwannabeyouanymore.mp3", "river_flows_in_you.mp3", "perfect.mp3"]
relax = ["beauty.mp3", "lazy_song.mp3", "nervous.mp3"]

mixer.init() # Initialise Mixer
mixer.music.set_volume(0.25) # Set Mixer volume

# Start up message (Inform start up so user won't think program has hung)
print("Starting WeatherCubed. Please wait...")
aiy.audio.say("Welcome to Weather Cubed. Started Successfully.")

def checkWeather():
    # Declare global variables
    global status, statusCode, temp, rainAlert
    # Get raw information from OpenWeatherMap
    print("--- [Debug: checkWeather] ---")
    owm = pyowm.OWM('94c1d42c12257fbc37a237c1609218ed') # API Key

    # Initialise location
    country = owm.weather_at_id(1880252)
    # Get Raw Weather info
    w = country.get_weather()

    status = w.get_detailed_status()                # Weather status (Readable)
    statusCode = int(w.get_weather_code())          # Weather status (Code)
    print("Parsed Status: " + status)               # [DEBUG] Print Status (Readable)
    print("Parsed Status Code: " + str(statusCode)) # [DEBUG] Print Status (Code)
    tempDict = w.get_temperature('celsius')         # Get Raw Temperature info
    print ("Raw Temperature Data: " + str(tempDict))# [DEBUG] Print Raw Temp
    temp = tempDict['temp']                         # Parse Temperature into variable

    print ("Parsed Temperature: " + str(temp))      # [DEBUG] Print Parsed Temperation
    print("--- --------------------- ---")


# Alert user when rain
def whenRainAlert():
    print("[INFO] Informing user that there is bad weather")

    # Random voice line (So it would sound natural)
    line = randint(1, 3)

    mixer.music.set_volume(.05) # Lower music volume

    # Play according to line chosen by random
    if line == 1:
        aiy.audio.say("Huh... There is going to be a " + status +  ". Make sure you bring an umbrella if you're going out soon! ")
    if line == 2:
        aiy.audio.say(status + " is going to happen soon. Make sure you have taken your laundry into the house.")
    if line == 3:
        aiy.audio.say("Close your windows, there's going to be some " + status)

    mixer.music.set_volume(.25) # Set music volume back

    # Turn light on
    aiy.voicehat.get_led().set_state(aiy.voicehat.LED.PULSE_QUICK)
    
    return()

# Governor: Handles excution of functions & time checks
def governor():
    # Declare global variables
    global status, statusCode, temp, rainAlert, hourPassAlert
    
    minTime = int(time.strftime("%M")) # Get time (only 'minute' portion)
    hourTime = int(time.strftime('%-H')) # Get time (only 'hour' portion)
    timeOfDay = str(time.strftime('%p')) # Get AM or PM

    # Call for weather update
    checkWeather()

    # Check status 2xx (Thunderstorm), 3xx (Drizzle), 5xx (Rain) [4xx - Empty group]
    if statusCode < 600 and rainAlert != True:
        rainAlert = True
        # Alert user
        whenRainAlert()
    elif statusCode > 600 and rainAlert == True: # If not raining
        rainAlert = False
        aiy.voicehat.get_led().set_state(aiy.voicehat.LED.OFF)

    # Check whether an hour has passed.
    if minTime == 0 and hourPassAlert == False:
        mixer.music.set_volume(.05) # Lower music volume
        print("[INFO] Informing user that an hour has passed")

        # Check if AM or PM
        # For 9AM onwards
        if timeOfDay == 'AM' and hourTime >= 9:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_Alarm.wav')
            # AIY say
            aiy.audio.say("It is now, " + str(hourTime) + 'in the morning; with ' + status + ". The temperature is " + str(temp) + "degrees celsius.")
        # For 12noon
        elif timeOfDay == 'PM' and hourTime == 12:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_PassDay.wav')
            # AIY say 
            aiy.audio.say("It is now, " + str(hourTime) + 'noon; with ' + status + ". The temperature is " + str(temp) + "degrees celsius.")
        # Before 6PM
        elif timeOfDay == 'PM' and hourTime < 18:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_Alarm.wav')
            # AIY say 
            aiy.audio.say("It is now, " + str(hourTime-12) + 'in the afternoon; with ' + status + ". The temperature is " + str(temp) + "degrees celsius.")
        # After 6PM
        elif timeOfDay == 'PM' and hourTime >= 18 and hourTime < 20:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_Alarm.wav')
            # AIY say 
            aiy.audio.say("It is now, " + str(hourTime-12) + 'in the evening; with ' + status + ". The temperature is " + str(temp) + "degrees celsius")
        # For 8PM
        elif timeOfDay == 'PM' and hourTime == 20:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_Alarm.wav')
            # AIY say 
            aiy.audio.say("It is now, " + str(hourTime-12) + 'in at night; with ' + status + ". The temperature is " + str(temp) + "degrees celsius.")
        # Special Bell for Passing day
        elif timeOfDay == 'AM' and hourTime == 0:
            # Alarm bell
            print("[INFO] Day passed - Playing special bell")
            aiy.audio.play_wave('./audio/WeatherCubed_PassDay.wav')

        # Silence all voiced notifications after 8PM alert and start annoucing at 9AM the next day onwards
        if hourTime >= 20 and hourTime < 9 and hourTime != 0:
            # Alarm bell
            aiy.audio.play_wave('./audio/WeatherCubed_Alarm.wav')
                    
        hourPassAlert = True
        mixer.music.set_volume(.25) # Set music volume back

    # Reset hourPassAlert boolean for next hour
    if minTime != 0:
        hourPassAlert = False

# Function to choose music from musicChoose
def music():
    mixer.music.set_volume(.05) # Lower music volume
    if statusCode < 600: # Rainy
        # Count number of songs in 'rain' and choose random
        trackNum = randint(0, len(rain) -1)
        aiy.audio.say("Now playing: Rainy Songs")
        mixer.music.load('./audio/rain/' + rain[trackNum])
        mixer.music.play()
    elif statusCode < 800: # Hazy
        # Count number of songs in 'moody' and choose random
        trackNum = randint(0, len(moody) -1)
        aiy.audio.say("Now playing: Moody Songs")
        mixer.music.load('./audio/moody/' + moody[trackNum])
        mixer.music.play()
    elif statusCode == 800: # Clear Skies
        # Count number of songs in 'happy' and choose random
        trackNum = randint(0, len(happy) -1)
        aiy.audio.say("Now playing: Happy Songs")
        mixer.music.load('./audio/happy/' + happy[trackNum])
        mixer.music.play()
    elif statusCode > 800: # Cloudy
        # Count number of songs in 'relax' and choose random
        trackNum = randint(0, len(relax) -1)
        aiy.audio.say("Now playing: Relax Songs")
        mixer.music.load('./audio/relax/' + relax[trackNum])
        mixer.music.play()
    mixer.music.set_volume(.25) # Set music volume back
    #buttonHandler() # Load buttonHandler so that is will accept button presses again
    return

##### Button Handler
button = aiy.voicehat.get_button()
def buttonHandler():
    button.wait_for_press()
    mixer.music.stop() # Stop music
    aiy.audio.say("Alright! Shuffling your playlist")
    print("[DEBUG] Button press registered")

    # Adapted from music()

    mixer.music.set_volume(.05) # Lower music volume
    if statusCode < 600: # Rainy
        aiy.audio.say("Reshuffling")
        # Count number of songs in 'rain' and choose random
        trackNum = randint(0, len(rain) -1)
        aiy.audio.say("Now playing: Rainy Songs")
        mixer.music.load('./audio/rain/' + rain[trackNum])
        mixer.music.play()
    elif statusCode < 800: # Hazy
        # Count number of songs in 'moody' and choose random
        trackNum = randint(0, len(moody) -1)
        aiy.audio.say("Now playing: Moody Songs")
        mixer.music.load('./audio/moody/' + moody[trackNum])
        mixer.music.play()
    elif statusCode == 800: # Clear Skies
        # Count number of songs in 'happy' and choose random
        trackNum = randint(0, len(happy) -1)
        aiy.audio.say("Now playing: Happy Songs")
        mixer.music.load('./audio/happy/' + happy[trackNum])
        mixer.music.play()
    elif statusCode > 800: # Cloudy
        # Count number of songs in 'relax' and choose random
        trackNum = randint(0, len(relax) -1)
        aiy.audio.say("Now playing: Relax Songs")
        mixer.music.load('./audio/relax/' + relax[trackNum])
        mixer.music.play()
    mixer.music.set_volume(.25) # Set music volume back

##### Music Choose
def musicChoose(): 
    if mixer.music.get_busy() == False: # Check if mixer is not playing
        print("[DEBUG] Choosing music")
        music()

##### Set AIY locale
aiy.i18n.set_language_code("en-US")

##### On start up, immediately fire the following:
# Main Function
governor()
# Monitor Music
music()

##### Schedulers
scheduler = BlockingScheduler()
scheduler.add_job(governor, 'interval', seconds=10) # Main Func
scheduler.add_job(musicChoose, 'interval', seconds=10) # Detect whether music is playing
scheduler.add_job(buttonHandler, 'interval', seconds=10) # Detect whether music is playing
scheduler.start()
