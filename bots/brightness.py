# to check da image for brightness
import sys,time
import Image
import ImageStat
import subprocess
sys.path.append('/home/access/Bloominglabs/web_admin/')
from pachube_updater import *
import eeml

IMAGE_FILE = '/home/access/Bloominglabs/bots/dumcam.jpeg'
IMAGE_GRAB = "streamer -c /dev/video0 -b 256 -o %s >/dev/null 2>/dev/null" % IMAGE_FILE
LightUnit = eeml.Unit('LightUnit', 'basicSI', 'LU')

def brightness(filename):
  im = Image.open(filename).convert('L')
  stat = ImageStat.Stat(im)
  return stat.rms[0]

def image_grab():
  p = subprocess.check_output(IMAGE_GRAB, shell=True)
  print p


if __name__ == '__main__':
  pac = Pachube('/v2/feeds/53278.xml')
  while True:
    image_grab()
    time.sleep(1)
    bright = brightness(IMAGE_FILE)
    print bright
    time.sleep(30) # 30 seconds is good
    if bright > 30: # get weird '16' readings
      pac.log('ServerRoomLight', bright, LightUnit)
