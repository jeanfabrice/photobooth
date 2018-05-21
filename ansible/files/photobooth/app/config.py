import subprocess
import os
import random


frames       = 1
counter      = 10
imagedir     = "/mnt/photobooth/capture.d"
montagedir   = "/mnt/photobooth"
withleds     = True
pressbutton  = True
knock        = True
knockservers = ['projector']

def render(source, dest):
  printpath = os.path.join(os.path.dirname(os.path.splitext(dest)[0]),'print')
  if not os.path.exists(printpath):
    os.makedirs(printpath)
  subprocess.check_call(['convert', source, '-resize', '1392x928', '-gravity', 'center', '-extent', '1748x1181+0+40', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cadre.png'), '-composite', dest])
  subprocess.check_call(['convert', dest, '-gravity', 'center', '-extent', '111%', os.path.join(printpath, os.path.basename(dest))])
