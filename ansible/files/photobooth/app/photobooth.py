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
from config import render
import config
import signal
from functools import partial
import fcntl
import socket

def knock(host, knock_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto('', (host, knock_port))
    except socket.error:
        pass

def handle_signal(camera, signum, frame):
    print ("\nCleaning camera link and exit")
    gp.check_result(gp.gp_camera_exit(camera))
    sys.exit(0)

def displayLed(c, f):
    print('counter: {0} - Left frame: {1}'.format(c, f))

def configurecamera(camera):
    setup = {"output": "PC", "viewfinder": 1}
    
    if config.frames > 1:
        setup['capturetarget'] = "card"
    
    for c, v in setup.items():
        print('setup "%s" camera property with value: %s'%(c,v))
        try:
            widget = gp.check_result(gp.gp_camera_get_single_config(camera,c))
        except gp.GPhoto2Error:
            print ('I/O error. Please restart camera')
            gp.check_result(gp.gp_camera_exit(camera))
            main()
        except:
            raise

        try:
            gp.check_result(gp.gp_widget_set_value(widget,v))
        except gp.GPhoto2Error:
            print ('I/O error. Please restart camera')
            gp.check_result(gp.gp_camera_exit(camera))
            main()
        except:
            raise

        try:
            gp.check_result(gp.gp_camera_set_single_config(camera,c,widget))
        except gp.GPhoto2Error:
            print ('I/O error. Please restart camera')
            gp.check_result(gp.gp_camera_exit(camera))
            main()
        except:
            raise

def captureSerie(camera,now):
    sequence     = []
    currentFrame = 0
    
    while currentFrame < config.frames:
        for c in xrange(config.counter,0,-1):
            displayLed(c,config.frames-currentFrame)
            time.sleep(1)
        
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

    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.ERROR)

    print('Start')
    
    try:
        gp.check_result(gp.use_python_logging())
    except:
        raise

    camera = gp.check_result(gp.gp_camera_new())

    signal.signal(signal.SIGTERM, partial(handle_signal,camera))
    signal.signal(signal.SIGINT, partial(handle_signal,camera))
    
    # Wait for camera to connect before continue
    while True:
        try:
            gp.check_result(gp.gp_camera_init(camera))
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print ('no camera, retry in 2 seconds')
                time.sleep(2)
                continue
            if ex.code == gp.GP_ERROR_IO:
                print ('I/O error. Restart camera, will retry in 5 seconds')
                time.sleep(5)
                continue
            if ex.code == gp.GP_ERROR_BAD_PARAMETERS:
                break
            raise
        break

    print('Camera connected!')
 
    try:
        configurecamera(camera)
    except:
        raise

    #Capture frame endlessly
    while True:
        try:
            time.sleep(10)
            #input("press button to continue")
        except SyntaxError:
            pass
        
        now = time.strftime("%Y%m%d_%Hh%Mm%Ss")
        
        capturedirectory = captureSerie(camera,now)
        
        try:
            config.render(os.path.join(capturedirectory,'*.jpg'), os.path.join(config.montagedir,'%s.jpg'%now))
        except:
            raise
        
        knock('projector', 10000)


if __name__ == "__main__":
    sys.exit(main())