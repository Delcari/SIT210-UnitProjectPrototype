import RPi.GPIO as GPIO
import _thread
import string 
import time

import math

import mqtt
import sensors


import kivy

kivy.require('1.11.0')

from kivy.app import App

from kivy.uix.gridlayout import GridLayout

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.uix.image import Image

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy_garden.graph import Graph, LinePlot

from kivy.uix.checkbox import CheckBox

from kivy.config import Config


#Borderless fullscreen
Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'fullscreen', 1)


#main screen
class MainScreen(GridLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        #Set the number of columns
        self.cols = 3

        #Heading
        self.add_widget(Label(size_hint=(1, 0.5)))
        self.heading = Label(size_hint=(1, 0.5))
        self.heading.font_size = 30
        self.heading.text = "Automatic Blinds & Live Weather"
        self.heading.bold = True

        self.add_widget(self.heading)
        self.add_widget(Label(size_hint=(1, 0.5)))

        #Current temperature label
        self.tempLabel = Label(size_hint=(1, 0.05))
        self.add_widget(self.tempLabel)

        self.add_widget(Label(size_hint=(1, 0.05)))

        #Current Humidity Label
        self.humLabel = Label(size_hint=(1, 0.05))
        self.add_widget(self.humLabel)

        #Graph theme
        graph_theme = {'background_color': (0,0,0,0), 'tick_color': (128/255,128/255,128/255,1)}

        #Temperature Graph
        self.tempGraph = Graph(xlabel='Time', ylabel='Temperature', x_ticks_minor=5, x_ticks_major=10, y_ticks_minor=1,y_ticks_major=5,x_grid_label=True, y_grid_label=True, padding=5, x_grid=True, y_grid=True,xmin=-0, xmax=60, ymin=-0, ymax=50, size_hint=(3, 1), **graph_theme)
        
        #Temperature plot (where to send the data points)
        self.tempPlot = LinePlot(color=(64/255,224/255,208/255 ,1), line_width=1.5)
        self.tempGraph.add_plot(self.tempPlot)
        
        self.add_widget(self.tempGraph)

        self.add_widget(Label())
        
        #Humidity Graph
        self.humGraph = Graph(xlabel='Time', ylabel='Humidity', x_ticks_minor=5, x_ticks_major=10, y_ticks_minor=1, y_ticks_major=10,x_grid_label=True, y_grid_label=True, padding=5, x_grid=True, y_grid=True,xmin=-0, xmax=60, ymin=-0, ymax=100, size_hint=(3, 1), **graph_theme)

        #Humidity plot (where to send the data points)
        self.humPlot = LinePlot(color=(64/255,224/255,208/255 ,1), line_width=1.5)

        self.humGraph.add_plot(self.humPlot)

        self.add_widget(self.humGraph)
        
        self.add_widget(Label())


        #Config button, sends you to the config screen
        self.button = Button(text="Configure",font_size=30, bold=True, size_hint=(3, 1))
        self.add_widget(self.button)

        #Starts a thread which collects the data from the sensor, then graphs it using 'PlotTempHum'
        _thread.start_new_thread(sensors.graphDHT11, (self.PlotTempHum,))

    def PlotTempHum(self, temp, hum, timeStamp, reset):
        #Resets the graph
        if (reset):
            self.tempPlot.points.clear()
            self.humPlot.points.clear()

        #updates the labels, (current temp/current hum)
        self.tempLabel.text = str(temp)
        self.humLabel.text = str(hum)

        #adds the points to the graph
        self.tempPlot.points.append((float(timeStamp), temp))
        self.humPlot.points.append((float(timeStamp), hum))



class Config(GridLayout):
    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)
        #Sets the number of columns
        self.cols=3

        #Title
        self.add_widget(Label(size_hint=(1, 0.5)))
        self.title = Label(text="Trigger Configuration", size_hint=(1, 0.5))
        self.title.font_size = 30
        self.title.bold = True
        self.add_widget(self.title)
        self.add_widget(Label(size_hint=(1, 0.5)))

        #Temperature checkbox heading  
        self.tempLabel = Label(size_hint=(0.8, 0.5))
        self.tempLabel.text ="Use Temp"
        self.tempLabel.bold = True
        self.tempLabel.font_size = 20
        self.add_widget(self.tempLabel)
        
        #Motion checkbox heading
        self.pirLabel = Label(size_hint=(0.8, 0.5))
        self.pirLabel.text ="Use Motion"
        self.pirLabel.bold = True
        self.pirLabel.font_size = 20
        self.add_widget(self.pirLabel)
        
        #Light checkbox heading
        self.lightLabel = Label(size_hint=(0.8, 0.5))
        self.lightLabel.text ="Use Light"
        self.lightLabel.bold = True
        self.lightLabel.font_size = 20
        self.add_widget(self.lightLabel)



        #create checkboxes
        self.checkbox = []
        #[temp, pir, light]
        for x in range(0,3):
            self.checkbox.append(CheckBox(size_hint=(0.8, 1)))
            self.add_widget(self.checkbox[x])
        
        #bind functions, which are called upon checkbox activation
        self.checkbox[0].bind(active=self.tempChecked)
        self.checkbox[1].bind(active=self.pirChecked)
        self.checkbox[2].bind(active=self.ldrChecked)

        #Main menu button, changes screen
        self.add_widget(Label(size_hint=(1, 0.75)))
        self.button= Button(text="Return to Main Menu", font_size=30, bold=True, size_hint=(3, 1))
        self.add_widget(self.button)
        self.add_widget(Label(size_hint=(1, 0.75)))

        #Starts a thread which starts listening for button presses on the controller
        _thread.start_new_thread(mqtt.listening, (self.checkTheBox,))


    #Checks a box based on what button is pressed on the controller
    def checkTheBox(self, index):
        #button 3 (manual blinds operation button)
        if (index == 3):
            self.uncheckBoxes()
            _thread.start_new_thread(sensors.BlindsManual, ())
        #checkbox is already on, stop the process and uncheck box
        elif (self.checkbox[index].active):
            self.uncheckBoxes()
            sensors.StopProcesses()
        #Check the selected box
        elif (index != 3):
            self.uncheckBoxes()
            self.checkbox[index].active = True




    #unchecks all the checboxes
    def uncheckBoxes(self, *args):
        for x in self.checkbox:
            x.active = False

    #if the temp checkbox is checked
    def tempChecked(self, checkboxInstance, isActive):  
        if (isActive):
            sensors.BlindsTemperature()

    #if the motion checkbox is checked
    def pirChecked(self, checkboxInstance, isActive):
        if (isActive):
            sensors.BlindsMotion()
        
    #f the light checkbox is checked
    def ldrChecked(self, checkboxInstance, isActive):
        if (isActive):
            sensors.BlindsLight()


        



class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)


        self.cols = 3

        #Main Screen
        self.mainScreen = Screen(name='main')
        #Configuration Screen
        self.config = Screen(name='new')

        self.add_widget(self.mainScreen)
        self.add_widget(self.config)


        mainScreen = MainScreen()

        #Change Screen -> Config
        mainScreen.button.bind(on_press=self.chConfig)

        self.mainScreen.add_widget(mainScreen)
        

        config = Config()

        #Change Screen -> Main Menu
        config.button.bind(on_press=self.chMainScreen)

        self.config.add_widget(config)
    
    #change the current screen to config
    def chConfig(self, *args):
        self.current='new'
    #change the current screen to main menu
    def chMainScreen(self, *args):
        self.current='main'



    


class MyApp(App):
    def build(self):
        self.title = 'Unit Project'
        return MyScreenManager()


MyApp().run()
GPIO.cleanup()
