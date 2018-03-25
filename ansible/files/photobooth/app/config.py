import subprocess
import os
import random


frames       = 1
counter      = 10
imagedir     = "capture.d"
montagedir   = "/mnt/photobooth"
withleds     = True
pressbutton  = True
knock        = True
knockservers = ['projector']

def render(source, dest):
  cadres = ['cadre.png', 'cadre1.png', 'cadre2.png', 'cadre3.png']
  printpath = os.path.join(os.path.dirname(os.path.splitext(dest)[0]),'print')
  if not os.path.exists(printpath):
    os.makedirs(printpath)
  subprocess.check_call(['convert', source, '-resize', '1300x867', '-gravity', 'center', '-rotate', '-2.3', '-extent', '1748x1181', os.path.join(os.path.dirname(os.path.realpath(__file__)), random.choice(cadres)), '-composite', dest])
  subprocess.check_call(['convert', dest, '-extent', '111%', '-gravity', 'center', os.path.join(printpath, os.path.basename(dest))])
