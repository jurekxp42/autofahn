#!/usr/bin/python
from __future__ import print_function
from __future__ import division
import sched
import time
import datetime
import os, sys, thread
import RPi.GPIO as GPIO
from pololu_drv8835_rpi import motors, MAX_SPEED
from autobahn.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.python import log
from twisted.internet import reactor
import random
import re
from socket import *
from threading import Thread


GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 17
GPIO_TRIGGER_M = 27

GPIO_ECHO_L = 23
GPIO_ECHO_M = 24

 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER_M, GPIO.OUT)

GPIO.setup(GPIO_ECHO_L, GPIO.IN)
GPIO.setup(GPIO_ECHO_M, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    GPIO.output(GPIO_TRIGGER_M, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    GPIO.output(GPIO_TRIGGER_M, False)
 
    StartTime_L = time.time()
    StartTime_M = time.time()
    StopTime_L = time.time()
    StopTime_M = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_L) == 0:
        StartTime_L = time.time()
    while GPIO.input(GPIO_ECHO_M) == 0:
        StartTime_M = time.time()

     
    # save time of arrival
    while GPIO.input(GPIO_ECHO_L) == 1:
        StopTime_L = time.time()
    while GPIO.input(GPIO_ECHO_M) == 1:
        StopTime_M = time.time()

        
    # time difference between start and arrival
    TimeElapsed_L = StopTime_L - StartTime_L
    TimeElapsed_M = StopTime_M - StartTime_M
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = [ ( (TimeElapsed_L * 34300) / 2 ) , ( (TimeElapsed_M * 34300) / 2 )  ]
 
    return distance

def loopMessage( self ):
    
    dist = distance()
    #print ("%.1f | " % dist[ 0 ] + "%.1f | "  % dist[ 1 ]  )
    self.sendMessage( '_fw_' + str( round( dist[ 0 ] ) ) , False )
    self.sendMessage( '_bw_' + str( round( dist[ 1 ] ) ) , False )
    time.sleep( 1 )
    loopMessage( self )

class MyServerProtocol(WebSocketServerProtocol):
    
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        #thread.start_new_thread( check_fw_distance , ( self , ) )

    def onOpen(self):
        print("WebSocket connection open.")
        loop = Thread(target=loopMessage, name="looper" ,  args=( self , ) )
        loop.start()
        

    def onMessage(self, action, isBinary):
        
        motors.setSpeeds(0, 0)
        time.sleep(0.05)
        #print( action )
        
        if action == 'st':
            motors.setSpeeds(0, 0)
            time.sleep(0.005)
            action = ''
        
        if action == 'ff':
            motors.setSpeeds(-20, -20)
            time.sleep(0.005)
            action = ''

        if action == 'bb':
            motors.setSpeeds(480, 480)
            time.sleep(0.005)
            action = ''

        if action == 'fl':
            motors.motor1.setSpeed(-20)
            motors.motor2.setSpeed( 240 )
            time.sleep(0.005)
            action = ''
                
        if action == 'fr':
            motors.motor1.setSpeed( 240 )
            motors.motor2.setSpeed( -20 )
            time.sleep(0.005)
            action = ''
            
        if action == 'bl':
            motors.motor1.setSpeed(480)
            motors.motor2.setSpeed( 120 )
            time.sleep(0.005)
            action = ''
        
                
        if action == 'br':
            motors.motor1.setSpeed( 120 )
            motors.motor2.setSpeed( 480 )
            time.sleep(0.005)
            action = ''
        

        if action == 'll':
            motors.motor1.setSpeed(-50)
            motors.motor2.setSpeed(480)
            time.sleep(0.005)
            action = ''
            
            
        if action == 'bll':
            motors.motor1.setSpeed(480)
            motors.motor2.setSpeed(-50)
            time.sleep(0.005)
            action = ''
            
         
        if action == 'rr':
            motors.motor1.setSpeed(480)
            motors.motor2.setSpeed(-50)
            time.sleep(0.005)
            action = ''
                
                
        if action == 'brr':
            motors.motor1.setSpeed(-50)
            motors.motor2.setSpeed(480)
            time.sleep(0.005)
            action = ''
            
        if action == 'takePicture':
            now = datetime.datetime.now()
            camera.capture( '/home/pi/images/robot_'+now.strftime("%Y_%m_%d_%H_%M")+'.jpg' )
            action = ''
            
        if action == 'cameraon':
            #print( "camera on" );
            os.system( '/home/pi/autofahn_server/start_camera.sh' )
            action = ''

        if action == 'cameraoff':
            #print( "camera off" );
            os.system( 'killall mjpg_streamer ' )
            action = ''
            
        if action == 'shutdown':
            os.system('halt')
            action = ''
            
        
        
    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        #thread.join()

    def resetMotor():
        motors.setSpeeds(0, 0)
        time.sleep(0.005)


if __name__ == '__main__':

    try:
        
        log.startLogging(sys.stdout)
        factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
        factory.protocol = MyServerProtocol
        reactor.listenTCP(9000, factory)
        reactor.run()
    
    except KeyboardInterrupt:
        pass
    

