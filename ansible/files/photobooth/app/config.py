import subprocess
import os
import random

frames     = 1
counter    = 2
imagedir   = "capture.d"
montagedir = "/mnt/photobooth"

def render(source, dest):
  cadres = ['cadre.png', 'cadre1.png', 'cadre2.png', 'cadre3.png']
  subprocess.check_call(['convert',source,'-resize','1300x867','-gravity','center','-rotate','-2.3','-extent','1748x1181ı',os.path.join(os.path.dirname(os.path.realpath(__file__)),random.choice(cadres)),'-composite', '-extent', '111%' ,dest])
