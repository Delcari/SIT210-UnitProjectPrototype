#PIR Motion Sensor\
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from datetime import datetime

from multiprocessing import Process, Value

from ctypes import c_bool
import stepper


print('Successfully Loaded Sensors')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#Motion Sensor PIN
PIR=12 

#AdaFruit uses GPIO.BCM pin# 23 instead of 16
#Temperature & Humidity Sensor PIN
DHT11=23

#Light Sensor PIN
LDR=18

#Boolean storing the value, which show if the blinds are opened or closed
blindsIsOpen = Value(c_bool, False)
#Flick to end a process
stop_process = Value(c_bool, False)
#Stores how many active processes there are
active_processes = Value('i', 0)

#Sets the PIR motion sensor as an input
GPIO.setup(PIR,GPIO.IN)

#Sets up the DHT11 temperature/humidity sensor
dht11Sensor=Adafruit_DHT.DHT11


#Trigger the blinds open/close
def TriggerBlinds():
    #adds a process 
    #(note: this isn't a process but is required for the manual opening of the blinds)
    active_processes.value += 1
    if(blindsIsOpen.value):
        print(datetime.now().strftime("%H:%M.%S") + " Closing blinds...")
    else:
        print(datetime.now().strftime("%H:%M.%S") + " Opening blinds...")

    #Operates the blinds, number of steps/direction
    stepper.OperateBlinds(2000, blindsIsOpen.value)

    #Updates the status of the blinds
    blindsIsOpen.value = not blindsIsOpen.value

    #removes the process once execution is finished
    active_processes.value -= 1

#graphs the temperature/hum values on the GUI
def graphDHT11(Graph):   
    #gets current hour
    hour = datetime.now().strftime("%H")
    Graph(0,0,0, False)
    while True:
        #read humidity, Temperature                                        
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11)

        #get datetime
        currentTime = datetime.now().strftime("%H:%M.%S")
        minuteSec = currentTime.split(':')[1]

        #if it ticks over to the next hour
        if (currentTime.split(':')[0] != hour):
            tempHum = []
            hour = currentTime.split(':')[0]
            #reset the graph
            Graph(temperature, humidity, minuteSec, True)
        else:
            Graph(temperature, humidity, minuteSec, False)

#reads the values from the temperature sensor
def ReadDHT11():
    #Adds a process
    active_processes.value += 1
    
    #wait until the other processes are finished
    while (active_processes.value > 1):
        time.sleep(0.2)

    stop_process.value = False
    print("DHT11 process started")
    while True:
        #read humidity/temperatured
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11)

        #Stop the Process
        if (stop_process.value): 
            print("DHT11 process closed")
            active_processes.value -= 1
            break
        #Temperature levels are low (room is cold)
        if (temperature < 20):
            #Blinds are closed 
            if (not blindsIsOpen.value):
                #Open blinds (let heat into the room)
                TriggerBlinds()
        #Temperature levels are high (room is warm)
        else:
            #blinds are open 
            if (blindsIsOpen.value):
                #Close blinds (trap heat)
                TriggerBlinds()


#reads the values from the light sensor
def ReadLight():
    #Adds a process
    active_processes.value += 1

    #wait until the other processes are finished
    while (active_processes.value > 1):
        time.sleep(0.2)
    
    stop_process.value = False
    print("Light process started")
    while True: 
        #Stop the Process
        if (stop_process.value):
            print("Light process closed") 
            active_processes.value -= 1
            break
        #reset the capacitor
        GPIO.setup(LDR, GPIO.OUT)
        GPIO.output(LDR, GPIO.LOW)
        time.sleep(2) 

        #set the starttime
        startTime = time.time()
        GPIO.setup(LDR, GPIO.IN)
        #wait until the pin changes value, then timestamp it
        while (GPIO.input(LDR) == GPIO.LOW):
            endTime = time.time()

        #light levels high
        #resistance low, (elapsed time short)
        if (endTime-startTime < 1):
            if (not blindsIsOpen.value):
                TriggerBlinds()
        #light levels low
        #resistance high, (elapsed time long)
        else:
            if (blindsIsOpen.value):
                TriggerBlinds()

#reads the values from the motion sensor
def ReadMotion():
    #Adds a Process
    active_processes.value += 1

    #wait until the other processes are finished
    while (active_processes.value > 1):
        time.sleep(0.2)

    stop_process.value = False

    #set the starttime 
    startTime = time.time()
    print("Motion process started")
    while True:
        time.sleep(0.5)
        isMotion = GPIO.input(PIR)

        #Stop the process
        if (stop_process.value): 
            print("Motion process closed")
            active_processes.value -= 1
            break
        #if theres movement
        if (isMotion):
            #reset the timer
            startTime = time.time()
            #if blinds are closed, open them
            if (not blindsIsOpen.value):
                TriggerBlinds()
        #if the the time has elapsed and the blinds are still open, close them
        if (time.time() - startTime > 30 and blindsIsOpen.value):
            TriggerBlinds()

#Stop the current processes
def StopProcesses():
    stop_process.value = True

#Create a process to run the 'ReadMotion' Function
def BlindsMotion():
    StopProcesses()
    p = Process(target=ReadMotion, args=())
    p.start()

#Create a process to run the 'ReadLight' Function
def BlindsLight():
    StopProcesses()
    p = Process(target=ReadLight, args=())
    p.start()

#Create a process to run the 'ReadDHT11' Function
def BlindsTemperature():
    StopProcesses()
    p = Process(target=ReadDHT11, args=())
    p.start()

#Create a process to run the 'TriggerBlinds' Function
def BlindsManual():
    StopProcesses()
    #wait till all the processes are closed
    while (not active_processes.value == 0):
        time.sleep(0.2)
    p = Process(target=TriggerBlinds, args=())
    p.start()
