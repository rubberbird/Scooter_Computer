#!/usr/bin/python
# Example using a character LCD plate.
from random import randint
import math
import os
from gps import *
from time import *
import time
import threading
import Adafruit_CharLCD as LCD

# Setup global variables
print "Setup GPS global var"
gpsd = None
lcd = None
logfile = None
buttons = None
log = None

def createLogfile():
   # Create a unique log file using random number because Pi doesn't know the time
   print "Generating Random Number"
   rndm_str = str(randint(2,999))
   global logfile
   logfile = '/home/pi/logs/gpslog-' + rndm_str + '.csv'
   global log
   log = open(logfile, "w+")
   # Add Header to CSV
   log.write( 'time,latitude,longitude,elevation,speed\n' )

   #Close file
   log.close()

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer


def setLCD(value):
   # Init LCD usign pins
   print "Updating LCD vi setLCD() Method"
   global lcd
   lcd = LCD.Adafruit_CharLCDPlate()

   lcd.clear()
   lcd.message(value)

   # define button array
   global buttons
   buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
            (LCD.LEFT,   'left'  , (1,0,0)),
            (LCD.UP,     'up'    , (1,0,1)),
            (LCD.DOWN,   'down'  , (1,1,0)),
            (LCD.RIGHT,  'right' , (1,0,1)) )

def startGps():
  # Starting GPS module
  lcd.clear()
  lcd.message('Starting GPS')
  time.sleep(1)
  global gpsp
  gpsp = GpsPoller() # create the thread
  gpsp.start() # start it up
  while True:
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc

      # open file to edit
      log = open(logfile, "a+")

      # Time
      time_str = str(gpsd.utc)

      # Convert Float to string
      speed_string = 'Speed: ' + str((gpsd.fix.speed * 3600) / 1000 ) + ' kmph'
      alt_string = 'Altitude: ' + str(gpsd.fix.altitude)
      lat_string = 'Lat: ' + str(gpsd.fix.latitude)
      long_string = 'Long: ' + str(gpsd.fix.longitude)

      # Plain Conversion for GPS Track File
      spd_str = str((gpsd.fix.speed * 3600) / 1000 )
      alt_str = str(gpsd.fix.altitude)
      lat_str = str(gpsd.fix.latitude)
      long_str = str(gpsd.fix.longitude)

      setLCD('Speed: ' + spd_str + '\n' + 'Loc: ' + lat_str + ',' + long_str)

      #Write Lat and Long to file
      log.write( time_str + ',' + lat_str + ',' + long_str + ',' + alt_str + ',' + spd_str + '\n' )

      if lcd.is_pressed(LCD.LEFT):
         time.sleep(1)
         setLCD('Killing GPS')
         gpsp.running = False
         #gpsp.join()
         print "Killing GPSP session"
         time.sleep(1)
         setLCD('GPS Stopped')
         log.close()
         print "Log Closed"
         #sys.exit()
         time.sleep(1)
         setLCD('Starting Main Loop')
         time.sleep(1)
         mainLoop()

      time.sleep(2) #set to whatever

def mainLoop():
  setLCD('Press a key!')
  #Loop through each button and check if it is pressed.
  while True:
    for button in buttons:
      if lcd.is_pressed(LCD.SELECT):
         lcd.clear()
         lcd.message('Started GPS')
         time.sleep(2)
         createLogfile()
         startGps()

      if lcd.is_pressed(LCD.LEFT):
         lcd.clear()
         lcd.message('Stopped GPS')
         gpsp.running = False
         gpsp.join()
         print "Killing GPSP session"
         setLCD('GPS Stopped')
         log.close()
         print "Log Closed"

# Working script -----------------------------------------------------------------

#Inital Greeting LCD
mainLoop();
