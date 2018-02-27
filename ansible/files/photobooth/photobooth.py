#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import subprocess
import sys
import gphoto2 as gp
import time
import uuid
import time

frames     = 1
counter    = 2
imagedir   = "capture.d"
montagedir = "montage.d"


def displayLed(c, f):
    print('counter: {0} - Left frame: {1}'.format(c, f))

def captureSerie(camera,now):
    sequence     = []
    currentFrame = 0
    while currentFrame < frames:
        for c in xrange(counter,0,-1):
            displayLed(c,frames-currentFrame)
            time.sleep(1)
        while True:
            try:
                file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE))
            except KeyboardInterrupt:
                return
            except gp.GPhoto2Error as ex:
                if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                    print ('no camera, try again in 2 seconds')
                    time.sleep(2)
                    continue
                if ex.code == gp.GP_ERROR_CAMERA_BUSY:
                    gp.check_result(gp.gp_camera_exit(camera))
                    gp.check_result(gp.gp_camera_init(camera))
                    time.sleep(2)
                    continue
                raise
            break
        sequence.append(file_path)
        currentFrame += 1
    capturedirectory = os.path.join(imagedir,now)
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
    if not os.path.exists(montagedir):
        os.makedirs(montagedir)
    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.ERROR)

    print('start capturing...')
    gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())

    # Wait endlessly for camera to connect then continue
    while True:
        try:
            gp.check_result(gp.gp_camera_init(camera))
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print ('no camera, try again in 2 seconds')
                time.sleep(2)
                continue
            raise
        break
    widget1 = gp.check_result(gp.gp_camera_get_single_config(camera,'output'))
    gp.check_result(gp.gp_widget_set_value(widget1,'PC'))
    gp.check_result(gp.gp_camera_set_single_config(camera,'output',widget1))
    widget2 = gp.check_result(gp.gp_camera_get_single_config(camera,'viewfinder'))
    gp.check_result(gp.gp_widget_set_value(widget2,1))
    gp.check_result(gp.gp_camera_set_single_config(camera,'viewfinder',widget2))
    widget3 = gp.check_result(gp.gp_camera_get_single_config(camera,'capturetarget'))
    gp.check_result(gp.gp_widget_set_value(widget3,'card'))
    gp.check_result(gp.gp_camera_set_single_config(camera,'capturetarget',widget3))
    #Capture frame endlessly
    while True:
        try:
            input("press enter to continue")
        except SyntaxError:
            pass
        except KeyboardInterrupt:
            break
        now = time.strftime("%Y%m%d_%Hh%Mm%Ss")
        try:
            capturedirectory = captureSerie(camera,now)
        except KeyboardInterrupt:
            break
        print("capture directory: %s"%capturedirectory)
        try:
            subprocess.check_call(['convert',os.path.join(capturedirectory,'*.jpg'),'-resize','1350x900','-gravity','center','-rotate','-2.4','-extent','1800x1200','cadre2.png','-composite',os.path.join(montagedir,'%s.jpg'%now)])
        except:
            raise
    print ("\nCleaning camera link and exit")
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())