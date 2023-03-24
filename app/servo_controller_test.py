import RPi.GPIO as GPIO			# using Rpi.GPIO module
from time import sleep			# import function sleep for delay
#GPIO.setmode(GPIO.BCM)			# GPIO numbering
GPIO.setwarnings(False)			# enable warning from GPIO
GPIO.setmode(GPIO.BOARD)
AN2 = 33				# set pwm2 pin on MD10-Hat
AN1 = 32				# set pwm1 pin on MD10-hat
DIG2 = 18				# set dir2 pin on MD10-Hat
DIG1 = 37				# set dir1 pin on MD10-Hat
GPIO.setup(AN2, GPIO.OUT)		# set pin as output
GPIO.setup(AN1, GPIO.OUT)		# set pin as output
GPIO.setup(DIG2, GPIO.OUT)		# set pin as output
GPIO.setup(DIG1, GPIO.OUT)		# set pin as output
sleep(1)				# delay for 1 seconds
p1 = GPIO.PWM(AN1, 100)			# set pwm for M1
p2 = GPIO.PWM(AN2, 100)			# set pwm for M2

try:					
  while True:

   print ("Left")				# display "Forward" when programe run
   GPIO.output(DIG1, GPIO.HIGH)		# set DIG1 as HIGH, M1B will turn ON
   GPIO.output(DIG2, GPIO.LOW)		# set DIG2 as HIGH, M2B will turn ON
   p1.start(20)			# set speed for M1 at 100%
   p2.start(20)			# set speed for M2 at 100%
   sleep(2)				#delay for 2 second
   print ("Forward")
   GPIO.output(DIG1, GPIO.LOW)          # set DIG1 as LOW, to control direction
   GPIO.output(DIG2, GPIO.LOW)          # set DIG2 as LOW, to control direction
   p1.start(20)                        # set speed for M1 at 100%
   p2.start(20)                        # set speed for M2 at 100%
   sleep(2)                             #delay for 2 second

   print ("Backward")
   GPIO.output(DIG1, GPIO.HIGH)         # set DIG1 as HIGH, to control direction
   GPIO.output(DIG2, GPIO.HIGH)         # set DIG2 as HIGH, to control direction
   p1.start(20)                        # set speed for M1 at 100%
   p2.start(20)                        # set speed for M2 at 100%
   sleep(2)                             #delay for 2 second

   print ("Right")
   GPIO.output(DIG1, GPIO.LOW)       
   GPIO.output(DIG2, GPIO.HIGH)    
   p1.start(20)                     
   p2.start(20)                   
   sleep(2)                        

   print ("STOP")
   GPIO.output(DIG1, GPIO.LOW)          # Direction can ignore
   GPIO.output(DIG2, GPIO.LOW)          # Direction can ignore
   p1.start(0)                          # set speed for M1 at 0%
   p2.start(0)                          # set speed for M2 at 0%
   sleep(3)                             #delay for 3 second


except:					# exit programe when keyboard interupt
   p1.start(0)				# set speed to 0
   p2.start(0)				# set speed to 0
   




   
# #!/usr/bin/env python3



# import RPi.GPIO as GPIO
# import time

# output_pins = {
#     'JETSON_XAVIER': 18,
#     'JETSON_NANO': 33,
#     'JETSON_NX': 33,
#     'CLARA_AGX_XAVIER': 18,
#     'JETSON_TX2_NX': 32,
#     'JETSON_ORIN': 18,
#     'JETSON_ORIN_NX': 33
# }
# output_pin = output_pins.get(GPIO.model, None)
# if output_pin is None:
#     raise Exception('PWM not supported on this board')


# def main():
#     print(output_pin)
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
#     p = GPIO.PWM(output_pin, 50)
#     val = 25
#     incr = 5
#     p.start(val)

#     print("PWM running. Press CTRL+C to exit.")
#     try:
#         while True:
#             time.sleep(1)
#             if val >= 100:
#                 incr = -incr
#             if val <= 0:
#                 incr = -incr
#             val += incr
#             p.ChangeDutyCycle(val)
#     finally:
#         p.stop()
#         GPIO.cleanup()

# def feed():
#     pass

# if __name__ == '__main__':
#     main()
