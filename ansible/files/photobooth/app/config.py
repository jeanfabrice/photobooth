import subprocess
import os

frames     = 1
counter    = 2
imagedir   = "capture.d"
montagedir = "montage.d"

def render(source, dest):
  subprocess.check_call(['convert',source,'-resize','1350x900','-gravity','center','-rotate','-2.4','-extent','1800x1200','cadre.png','-composite',dest])
