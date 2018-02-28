#!/usr/bin/env python
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
        except:
            raise
        try:
            gp.check_result(gp.gp_widget_set_value(widget,v))
        except:
            raise
        try:
            gp.check_result(gp.gp_camera_set_single_config(camera,c,widget))
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
            except KeyboardInterrupt:
                return
            except gp.GPhoto2Error as ex:
                if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                    print ('no camera, retry in 2 seconds')
                    time.sleep(2)
                    continue
                if ex.code == gp.GP_ERROR_CAMERA_BUSY:
                    print ('camera seems busy. Resetting and retry in 2 seconds')
                    gp.check_result(gp.gp_camera_exit(camera))
                    gp.check_result(gp.gp_camera_init(camera))
                    time.sleep(2)
                    continue
                raise
            break
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

    # Wait endlessly for camera to connect then continue
    while True:
        try:
            gp.check_result(gp.gp_camera_init(camera))
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print ('no camera, retry in 2 seconds')
                time.sleep(2)
                continue
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
            input("press button to continue")
        except SyntaxError:
            pass
        except KeyboardInterrupt:
            break
        
        now = time.strftime("%Y%m%d_%Hh%Mm%Ss")
        
        try:
            capturedirectory = captureSerie(camera,now)
        except KeyboardInterrupt:
            break
        
        try:
            config.render(os.path.join(capturedirectory,'*.jpg'), os.path.join(config.montagedir,'%s.jpg'%now))
        except:
            raise

    print ("\nCleaning camera link and exit")
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())