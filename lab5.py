import RPi.GPIO as GPIO
import time
import math

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

pinouts = range(17, 27)
pwmobjs = []

for p in pinouts:
  GPIO.setup(p, GPIO.OUT)
  pwmobjs.append(GPIO.PWM(p, 500))

# for callback
p_in = 13
direction = 1;
GPIO.setup(p_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def flip_directions(p_in):
  global direction
  direction *= -1

GPIO.add_event_detect(p_in, GPIO.RISING, callback=flip_directions, bouncetime = 1000)

try:
  for i in range(len(pinouts)):
    pwmobjs[i].start(0)
  
  while 1:
    for i in range(len(pinouts)):
      B = math.pow( math.sin(2.0*3.1415*0.2*time.time() + 3.14159 / 11.0 * i * direction) , 2) * 100.0
      pwmobjs[i].ChangeDutyCycle(B)
except KeyboardInterrupt:
  print('\nExiting')
