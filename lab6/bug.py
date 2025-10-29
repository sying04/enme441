import RPi.GPIO as GPIO
import time
import random
from shifter import Shifter

GPIO.setmode(GPIO.BCM)

dataPin, latchPin, clockPin = 23, 24, 25

class Bug:
  def __init__(self, dataPin, latchPin, clockPin, timestep = 0.1, x = 3, isWrapOn = False):
    self.timestep = timestep
    self.x = x
    self.isWrapOn = isWrapOn
    self.__shifter = Shifter(dataPin, latchPin, clockPin)
    self.isRunning = False
  
  def start(self):
    self.isRunning = True

  def stop(self):
    self.isRunning = False

  def changeWrap(self):
    self.isWrapOn = not self.isWrapOn
	
  def setSpeed(self, newSpeed):
    self.timestep = newSpeed

  def move(self):
    if(not self.isRunning): 
      self.__shifter.shiftByte(0b00000000)
      return

    if(random.random() < 0.5):
      if(self.x >= 7):
        if(self.isWrapOn): self.x = 1
      else:
        self.x += 1

    else:
      if(self.x <= 1):
        if(self.isWrapOn): self.x = 7      
      else:
        self.x -= 1 

    self.__shifter.shiftByte(2**self.x)
    time.sleep(self.timestep)

# callbacks
s1 = 13
s2 = 19
s3 = 26

GPIO.setup(s1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def changeWrap(s2):
  global bug
  bug.changeWrap()

GPIO.add_event_detect(s2, GPIO.BOTH, callback=changeWrap, bouncetime = 100)

bug = Bug(dataPin, latchPin, clockPin)

try:
 while 1:
  if(GPIO.input(s1)):
    bug.start()
  else:
    bug.stop()

  if(GPIO.input(s3)):
    bug.setSpeed(0.03)
  else:
    bug.setSpeed(0.1)

  bug.move()
except:
 GPIO.cleanup()
