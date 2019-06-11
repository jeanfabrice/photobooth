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
  cadres = ['cadre-vert.png', 'cadre-rouge.png', 'cadre-bleu.png']
  printpath = os.path.join(os.path.dirname(os.path.splitext(dest)[0]),'print')
  if not os.path.exists(printpath):
    os.makedirs(printpath)
  subprocess.check_call(['convert', source, '-strip', '-resize', '1260x840', '-gravity', 'center', '-extent', '1748x1181', os.path.join(os.path.dirname(os.path.realpath(__file__)), random.choice(cadres)), '-composite', dest])
