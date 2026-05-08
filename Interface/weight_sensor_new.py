import RPi.GPIO as gpio
import time


DT =27
SCK=17

def readCount():
  i=0
  Count=0
  gpio.setup(DT, gpio.OUT)
  gpio.output(DT,1)
  gpio.output(SCK,0)
  gpio.setup(DT, gpio.IN)
  while gpio.input(DT) == 1:
      i=0
  for i in range(24):
        gpio.output(SCK,1)
        Count=Count<<1
        gpio.output(SCK,0)
        #time.sleep(0.001)
        if gpio.input(DT) == 0: 
            Count=Count+1      
  gpio.output(SCK,1)
  Count=Count^0x800000
  gpio.output(SCK,0)
  return Count 

while 1:
  count= readCount()
  w=0
  w=(count-sample)/106
  print(w,"g")
  time.sleep(0.5)


