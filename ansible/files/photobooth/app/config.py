import subprocess
import os
import random

frames     = 1
counter    = 2
imagedir   = "capture.d"
montagedir = "/mnt/photobooth"

def render(source, dest):
  cadres = ['cadre.png', 'cadre1.png', 'cadre2.png', 'cadre3.png']
  subprocess.check_call(['convert',source,'-resize','1350x900','-gravity','center','-rotate','-2.4','-extent','1800x1200',os.path.join(os.path.dirname(os.path.realpath(__file__)),random.choice(cadres)),'-composite',dest])
