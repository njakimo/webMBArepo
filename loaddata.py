import django
import seriesbrowser
import os
import random
import re
import pickle

from seriesbrowser.models import Brain
from seriesbrowser.models import Laboratory
from seriesbrowser.models import Series
from seriesbrowser.models import Section
from seriesbrowser.models import Tracer
from seriesbrowser.models import Injection
from seriesbrowser.models import LabelMethod
from seriesbrowser.models import ImageMethod
from seriesbrowser.models import Region
from seriesbrowser.models import SectioningPlane
from seriesbrowser.models import DataResolver

class Mouse:
   def __init__(self, Name,Injdate,Tracer,LabelMethod,Injvolume,Injvolunits, Xcoord, Ycoord, Zcoord):
      self.name = Name
      self.injdate = Injdate
      self.tracer = Tracer
      self.labelMethod = LabelMethod
      self.injvolume = Injvolume
      self.injvolunits= Injvolunits
      self.xcoord = Xcoord
      self.ycoord = Ycoord
      self.zcoord = Zcoord
   def __unicode__(self):
      return self.name  

class Bams:
   def __init__(self, RatId, RatCode, MouseId, MouseCode):
      self.ratid = RatId
      self.ratcde = RatCode
      self.mouseid = MouseId
      self.mousecode = MouseCode
   def __unicode__(self):
      return self.mouseCode  
     
limsf = open('../csvfiles/lims_2011_04_04.txt', 'r')
dsf = open('../csvfiles/datasummary.csv', 'r')
araf = open('../csvfiles/allen_reference_atlas.csv', 'r')
errorf = open('../csvfiles/load_error.txt', 'w')
bamsf = open('../csvfiles/bams.csv', 'r')

ara25umFile = open("../pckfiles/ara25um.pck", "r")
ara25um = pickle.load(ara25umFile)
#labelsFile = open("../pckfiles/labelsLookup.pck", "r")
#labelLookup = pickle.load(labelsFile)

orgn = {'x':228, 'y':221, 'z':36}

r = random.seed()

aralist = []
bamsDict = {}

#load data from bams
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
    aralist.append(r)

# load data from lims
limslist = []
namelist = []
for sline in limsf:
   sarray = sline.split(',')
  # errorf.write(sarray[12]+'\n')
   try: 
     if sarray[12].strip() == 'Imaged':
        #marray = sarray[0].split(' ')
        #errorf.write('Mouse ' + sarray[0]+ '\n')
        marray = sarray[0].split(' ')
        n = marray[0].strip()+ '' + marray[1].strip()        
        if marray[0].strip() == 'PMD':
        #  errorf.write(' ** ' + sarray[7] + '\n')
        #  errorf.write('Mouse ' + n + '\n')
          iarray = sarray[7].split(' ')
        
          mouse = Mouse(n, sarray[1], sarray[2],sarray[11].strip(),iarray[0].strip(), 'nl', sarray[3].strip(), sarray[4].strip(), sarray[5].strip())
          limslist.append(mouse)
          namelist.append(n)
   except:
      pass      
      #errorf.write('Error !!!! ' + sline + '\n' )
      #traceback.print_exc()

#errorf.write('@@@@@@@@@@@@@@')
 
lab_m = Laboratory(name='mitralab')
lab_m.save()

sp_s= SectioningPlane(desc='Sagittal')
sp_s.save()
sp_c = SectioningPlane(desc='Coronal')
sp_c.save()
sp_h = SectioningPlane(desc='Horizontal')
sp_h.save()

lm_n = LabelMethod(name='Nissl')
lm_n.save()
lm_f = LabelMethod(name='Flourescent')
lm_f.save()
lm_ihc = LabelMethod(name='IHC')
lm_ihc.save()

im_b = ImageMethod(name='Brightfield')
im_b.save()
im_f = ImageMethod(name='Flourescent')
im_f.save()

slist = os.listdir('/mnt/data001/MBAProcessingResults/PMD')


for sr in slist:

    if sr.startswith('PMD17') or sr.startswith('PMD18') or sr.startswith('PMD113') or sr.startswith('PMD114'):
       brain = Brain(name=sr)
       brain.save()

       numSections = (len(os.listdir('/mnt/data001/MBAProcessingResults/PMD/'+sr))-1)/2

       #sampleSectionNum = random.randrange(1,numSections)

       #errorf.write(' sample section num ' + str(sampleSectionNum) + '\n')

       series_n = Series(desc=brain.name + ' Nissl Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu' ,lab_id=lab_m.id, labelMethod_id = lm_n.id, imageMethod_id = im_b.id, sectioningPlane_id=sp_c.id, numQCSections = 0)
       series_n.save()

       series_f = Series(desc=brain.name + ' Flourescent Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu', lab_id=lab_m.id, labelMethod_id = lm_f.id, imageMethod_id = im_f.id, sectioningPlane_id=sp_c.id, numQCSections = 0)
       series_f.save()

       series_ihc = Series(desc=brain.name + ' IHC Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu' ,lab_id=lab_m.id, labelMethod_id = lm_ihc.id, imageMethod_id = im_b.id, sectioningPlane_id=sp_c.id, numQCSections = 0)
       series_ihc.save()

      
       for l in limslist:
          if l.name == sr:
             tn = l.tracer
             tracer = Tracer(name=tn)
             try:
      #         errorf.write('Match found : ' + sr + ' - ' + tn + '\n')
              # tracer is unique by name. If already exists, write will fail. 
               try:
                 tracer.save()
               except:
                 pass
               if l.labelMethod.find("Flou") != -1:
                 idSeries = series_f.id
               elif l.labelMethod.find("IHC") != -1:
                 idSeries = series_ihc.id
               injectionID = ara25um[orgn['x']+round(float(l.xcoord)*1000/25),orgn['z']+round(float(l.zcoord)*1000/25),orgn['y']+round(float(l.ycoord)*1000/25)]
               injection = Injection(series_id = idSeries, region_id = injectionID, tracer_id = Tracer.objects.get(name=tn).id, volume=l.injvolume, volumeUnits=l.injvolunits, x_coord = l.xcoord, y_coord = l.ycoord, z_coord = l.zcoord)
               injection.save()
               break
             except:
               errorf.write('Cannot save ' + sr + ' - ' + tn + '\n')

       sclist = os.listdir('/mnt/data001/MBAProcessingResults/PMD/'+sr)

       dist2injN = 100
       dist2injF = 100
       dist2injIHC = 100

       ydict = {}
       with open('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/ydist.txt') as f:
          for line in f:
                m = re.match(r"(meta_.*txt)\:\s+(-?\d+.\d+)", line)
                ydict[m.group(1)] = m.group(2)

       for sc in sclist:
          if sc.startswith('meta'):
                scOrder = sc[sc.rfind("_")+1:sc.find(".txt")]
                scImage = sc[sc.find("_")+1:sc.find(".txt")]

                scName = sc[5:len(sc)-4]
                metaName = ''

                #try:
                metaName = '/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sc 
                metaf=open(metaName)

                metal = metaf.readline()

                if metal.find(' N ') != -1:
                   idSeries = series_n.id
                   bitDepth = 8
                   series_n.numQCSections += 1

                elif metal.find(' F ') != -1:
                   idSeries = series_f.id
                   bitDepth = 16
                   series_f.numQCSections += 1
		          
                elif metal.find(' IHC ') != -1:
                   idSeries = series_ihc.id
                   bitDepth = 8
                   series_ihc.numQCSections += 1
                
                if os.path.exists('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2'):
              		section = Section(series_id=idSeries, name=sr+'_'+scOrder, sectionOrder=scOrder, pngPathLow='/brainimg/'+sr+'/'+sr+'_'+scOrder+'.jpg', jp2Path='/brainimg/'+sr+'/'+sr+'_'+scOrder+'.jp2',jp2FileSize=os.path.getsize('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2'), jp2BitDepth=bitDepth, y_coord=ydict[sc])
              		dataresolver = DataResolver(identifier='PMD/'+sr+'_'+scOrder , imageFile='/brainimg/'+sr+'/'+sr+'_'+scOrder+'.jp2')

              		section.save()
              		dataresolver.save()
              		idSection = section.id
              		dist2injSec = abs(float(ydict[sc])-float(l.ycoord))

              		if metal.find(' N ') != -1 and dist2injSec < dist2injN:
              		   series_n.sampleSection_id = idSection
              		   dist2injN = dist2injSec

              		elif metal.find(' F ') != -1 and dist2injSec < dist2injF:
              		   series_f.sampleSection_id = idSection
              		   dist2injF = dist2injSec
							  
              		elif metal.find(' IHC ') != -1 and dist2injSec < dist2injIHC:
              		   series_ihc.sampleSection_id = idSection
              		   dist2injIHC = dist2injSec

                else:
                    errorf.write('File not found : ' +sr+'_'+scOrder+'.jp2'+ '\n')
                #   erirorf.write('File not found: \n')

       series_n.save()
       series_f.save()
       series_ihc.save()