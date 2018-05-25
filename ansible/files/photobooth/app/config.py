import subprocess
import os
import random
import cups


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
  subprocess.check_call(['convert', source, '-strip', '-resize', '1200x819', '-gravity', 'center', '-extent', '1800x1200', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cadre.png'), '-composite', dest])

