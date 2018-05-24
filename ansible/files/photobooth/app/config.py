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

def printPic(fileName):
    conn = cups.Connection()
    printers = conn.getPrinters()
    default_printer = printers.keys()[0]
    cups.setUser('pi')
    conn.printFile (default_printer, fileName, "", {'raw':'True', 'StpImageType/Image':'Photo', 'StpBorderless/Borderless':'True' })

def render(source, dest):
  printpath = os.path.join(os.path.dirname(os.path.splitext(dest)[0]),'print')
  if not os.path.exists(printpath):
    os.makedirs(printpath)
  subprocess.check_call(['convert', source, '-strip', '-resize', '1200x819', '-gravity', 'center', '-extent', '1800x1200', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cadre.png'), '-composite', dest])
  #subprocess.check_call(['convert', dest, '-strip', '-gravity', 'center', '-extent', '111%', os.path.join(printpath, os.path.basename(dest))])
  printPic(dest)

