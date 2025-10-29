import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class Shifter:
  def __init__(self, dataPin, clockPin, latchPin):
    self.dataPin = dataPin
    self.clockPin = clockPin
    self.latchPin = latchPin
    
    GPIO.setup(self.dataPin, GPIO.OUT)
    GPIO.setup(self.latchPin, GPIO.OUT, initial=0) # start latch & clock low
    GPIO.setup(self.clockPin, GPIO.OUT, initial=0)
    
  def __ping(self, p): # ping the clock or latch pin
   GPIO.output(p,1)
   time.sleep(0)
   GPIO.output(p,0)
     
  def shiftByte(self, b): # send a byte of data to the output
   for i in range(8):
    GPIO.output(self.dataPin, b & (1<<i))
    self.__ping(self.clockPin) # add bit to register
   self.__ping(self.latchPin) # send register to output
