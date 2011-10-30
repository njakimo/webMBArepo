import django
import seriesbrowser
import os
import random
import re
import pickle
import sys

from seriesbrowser.models import Region

class Bams:
   def __init__(self, RatId, RatCode, MouseId, MouseCode):
      self.ratid = RatId
      self.ratcde = RatCode
      self.mouseid = MouseId
      self.mousecode = MouseCode
   def __unicode__(self):
      return self.mouseCode  
     
araf = open('../csvfiles/allen_reference_atlas.csv', 'r')
bamsf = open('../csvfiles/bams.csv', 'r')
errorf = open('../csvfiles/bams_load_error.txt', 'w')

#load data from bams
bamsDict = {}
for b in bamsf:
    br = b.split(",")
    bobj = Bams(br[0],br[1], br[3],br[4])
    errorf.write('adding code ** ' + bobj.mousecode + '\n') 
    bamsDict[bobj.mousecode] = bobj

#load data from ARA
for ara in araf:
    ar = ara.split(",")
    mouseCode = ar[2].strip()
    bMouseId = 0
    bRatId = 0
    try:    
      if bamsDict[mouseCode]:
        errorf.write('for code ** ' + mouseCode + '\n') 
        bMouseId = bamsDict[mouseCode].mouseid
        bRatId = bamsDict[mouseCode].ratid
    except:
      errorf.write(' not found code ** ' + mouseCode + '\n') 
      pass
    errorf.write('for code ' + mouseCode + ' mouse id ' + str(bMouseId) + ' rat id ' + str(bRatId) + '\n')
    r = Region(id=ar[0],code=ar[2].strip(), desc=ar[1].strip(),parent_id=ar[3],bamsMouseId = bMouseId, bamsRatId = bRatId, leftId=ar[4],rightId=ar[5])
    r.save()
