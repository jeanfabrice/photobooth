#!/usr/bin/env python -u
#-*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import sys
import gphoto2 as gp
import time
import uuid
import time
import config
import signal
from functools import partial
import socket
import RPi.GPIO as GPIO

tensleds      = [27, 4, 17, 22]
unitsleds     = [11, 10, 9, 5]
frameleds     = [19, 6, 13,26]
buttonled     = 14
buttonswitch  = 18

def displayNumOn7Segments(num, segment):
    binnum = "{0:04b}".format(num)
    for idx, val in enumerate(binnum):
        GPIO.output(segment[idx], GPIO.LOW if val=='0' else GPIO.HIGH)

def countdown(start):
    for c in xrange(start, 0, -1):
        if config.withleds:
            displayNumOn7Segments(int(c/10), tensleds)
            displayNumOn7Segments(c%10, unitsleds)
            switchLed(buttonled, 'on' if c%2 else 'off')
        else:
            print(c)
        time.sleep(1)
    if config.withleds:
        displayNumOn7Segments(0, unitsleds)
    else:
        print(0)

def switchLed(channel, state='on'):
    GPIO.output(channel, GPIO.HIGH if state=='on' else GPIO.LOW)

def initGPIO():
    if config.pressbutton or config.withleds:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for channel in tensleds+unitsleds+frameleds+[buttonled]:
            GPIO.setup(channel, GPIO.OUT)
        for channel in [buttonswitch]:
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def knock(host, knock_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto('', (host, knock_port))
    except socket.error:
        pass

def handle_signal(camera, signum, frame):
    print ("\nCleaning camera link and exit")
    gp.check_result(gp.gp_camera_exit(camera))
    GPIO.cleanup()
    sys.exit(0)

def wairForButtonPressed():
    while True:
        input_state = GPIO.input(buttonswitch)
        if input_state == False:
            switchLed(buttonled, 'off')
            break

def blank7Segments():
    if config.withleds:
        displayNumOn7Segments(10, tensleds)
        displayNumOn7Segments(10, unitsleds)
        displayNumOn7Segments(10, frameleds)

def configurecamera(camera):
    setup = {
        "viewfinder": 1,
        "output": "TFT"
    }
    
    if config.frames > 1:
        setup['capturetarget'] = "card"
    
    for c, v in setup.items():
        print('Setting up "%s" camera property with value: %s'%(c,v))
        try:
            widget = gp.check_result(gp.gp_camera_get_single_config(camera,c))
            gp.check_result(gp.gp_widget_set_value(widget,v))
            gp.check_result(gp.gp_camera_set_single_config(camera,c,widget))
            time.sleep(2)
        except gp.GPhoto2Error:
            print ('I/O error. Please restart camera')
            gp.check_result(gp.gp_camera_exit(camera))
            main()
        except:
            raise
    print('Done')

def captureFrame(camera,now):
    sequence     = []
    currentFrame = 0
    
    while currentFrame < config.frames:
        countdown(config.counter)
        switchLed(buttonled, 'off')
        while True:
            try:
                file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE))
            except gp.GPhoto2Error as ex:
                if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                    print ('no camera, retry in 2 seconds')
                    time.sleep(2)
                    continue
                if ex.code == gp.GP_ERROR_CAMERA_BUSY:
                    print ('camera seems busy. retry in 2 seconds')
                    time.sleep(2)
                    continue
                raise
            break
        print("Photo taken")
        sequence.append(file_path)
        currentFrame += 1
        if config.withleds:
            displayNumOn7Segments(config.frames-currentFrame, frameleds)
        else:
            print('Left frame: {0}'.format(config.frames-currentFrame))
    
    capturedirectory = os.path.join(config.imagedir,now)
    
    if not os.path.exists(capturedirectory):
        os.makedirs(capturedirectory)
    
    for idx,frame in enumerate(sequence):
        target = os.path.join(capturedirectory, '%s.jpg'%idx)
        try:
            camera_file = gp.check_result(gp.gp_camera_file_get(camera, frame.folder, frame.name, gp.GP_FILE_TYPE_NORMAL))
        except:
            raise
        
        try:
            gp.check_result(gp.gp_file_save(camera_file, target))
        except:
            raise
    print("Photo saved")
    return capturedirectory


def main():
    if not os.path.exists(config.montagedir):
        os.makedirs(config.montagedir)

    initGPIO()

    blank7Segments()

    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.ERROR)

    print('Start')
    
    try:
        gp.check_result(gp.use_python_logging())
    except:
        raise

    #create camera object
    camera = gp.check_result(gp.gp_camera_new())

    # Handle SIGTERM and SIGINT to properly reset and exit camera before dying
    signal.signal(signal.SIGTERM, partial(handle_signal,camera))
    signal.signal(signal.SIGINT, partial(handle_signal,camera))
    
    # Wait for camera to connect before continuing
    while True:
        try:
            gp.check_result(gp.gp_camera_init(camera))
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print ('camera not detected, retrying in 2 seconds')
                time.sleep(2)
                continue
            if ex.code == gp.GP_ERROR_IO:
                print ('I/O error. Restart camera, retrying in 5 seconds')
                time.sleep(5)
                continue
            #if ex.code == gp.GP_ERROR_BAD_PARAMETERS:
            #    break
            blank7Segments()
            raise
        except:
            blank7Segments()
            raise
        break

    print('Camera connected')
 
    try:
        configurecamera(camera)
    except:
        blank7Segments()
        raise

    #Capture frame endlessly
    while True:
        if config.withleds:
            displayNumOn7Segments(int(config.counter/10),tensleds)
            displayNumOn7Segments(config.counter%10,unitsleds)
            displayNumOn7Segments(config.frames,frameleds)

        if config.pressbutton:
            switchLed(buttonled)
            wairForButtonPressed()

        #define current time to timestamp frame name
        now = time.strftime("%Y%m%d_%Hh%Mm%Ss")
        
        capturedirectory = captureFrame(camera,now)
        
        try:
            #Call rendering method from config module with source file list and destination file path
            config.render(os.path.join(capturedirectory,'*.jpg'), os.path.join(config.montagedir,'%s.jpg'%now))
        except:
            raise
        
        if config.knock:
            for knockserver in config.knockservers:
                knock(knockserver, 10000)


if __name__ == "__main__":
    sys.exit(main())
