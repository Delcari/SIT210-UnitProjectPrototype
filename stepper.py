import time
import RPi.GPIO as GPIO

print('\nSuccessfully Loaded Stepper')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


#Motor Driver
IN1=7 # IN1
IN2=11 # IN2
IN3=13 # IN3
IN4=15 # IN4


#Set the pins as outputs
GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)
GPIO.setup(IN3,GPIO.OUT)
GPIO.setup(IN4,GPIO.OUT)

#Set them all to LOW
GPIO.output(IN1, False)
GPIO.output(IN2, False)
GPIO.output(IN3, False)
GPIO.output(IN4, False)

#The 28BYJ-48 Motor Sequence
Sequence = [
[0, 0, 0, 1],
[0, 0, 1, 1],
[0, 0, 1, 0],
[0, 1, 1, 0],
[0, 1, 0, 0],
[1, 1, 0, 0],
[1, 0, 0, 0],
[1, 0, 0, 1]
]

#Operate the blinds
def OperateBlinds(n, isOpen):
        #if they're open, close them
        if(isOpen):
            #Cycle through the sequence 'n' # of times
            for i in range(int(n)):
                for j in range(len(Sequence)):
                    GPIO.output(IN1, Sequence[j][0])
                    GPIO.output(IN2, Sequence[j][1])
                    GPIO.output(IN3, Sequence[j][2])
                    GPIO.output(IN4, Sequence[j][3])
                    time.sleep(0.001)
        #if they're closed, open them
        else:
            #Cycle through the sequence 'n' # of times
            for i in range(int(n)):
                for j in (range(len(Sequence))):
                    GPIO.output(IN1, Sequence[j][3])
                    GPIO.output(IN2, Sequence[j][2])
                    GPIO.output(IN3, Sequence[j][1])
                    GPIO.output(IN4, Sequence[j][0])
                    time.sleep(0.001)
