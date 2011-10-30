import os
import random
import re
import pickle
import sys

class Mouse:
   def __init__(self, Name,Injdate,Tracer,LabelMethod,Injvolume,Injvolunits, Xcoord, Ycoord, Zcoord):
      self.name = Name
      self.injdate = Injdate
      self.tracer = Tracer
      self.labelMethod = LabelMethod
      self.injvolume = Injvolume
      self.injvolunits = Injvolunits
      self.xcoord = Xcoord
      self.ycoord = Ycoord
      self.zcoord = Zcoord
   def __unicode__(self):
      return self.name  

lims_path = '../csvfiles/lims_dump_2011_08_10_9485.txt'
limsf = open(lims_path, 'r')

series2limsDict = {}
for sline in limsf:
   sarray = sline.split(',')
   try: 
     if sarray[12].strip() == 'Imaged':
        marray = sarray[0].split(' ')
        n = marray[0].strip()+ '' + marray[1].strip()        
        if marray[0].strip() == 'PMD':
          iarray = sarray[7].split(' ')
          mouse = Mouse(n, sarray[1], sarray[2],sarray[11].strip(),iarray[0].strip(), 'nl', 
			sarray[3].strip(), sarray[4].strip(), sarray[5].strip())
          series2limsDict['MouseBrain_' + str(marray[1].strip()).zfill(4)] = mouse
   except:
      pass 

pickle.dump(series2limsDict, open( "../pckfiles/series2limsDict.p", "wb" ) )
