import django
import seriesbrowser
import os
import random

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
      
limsf = open('../csvfiles/lims_2011_04_04.txt', 'r')
dsf = open('../csvfiles/datasummary.csv', 'r')
araf = open('../csvfiles/allen_reference_atlas.csv', 'r')
errorf = open('../csvfiles/load_error.txt', 'w')

r = random.seed()

aralist = []

#load data from ARA
for ara in araf:
    ar = ara.split(",")
    r = Region(id=ar[0],code=ar[2].strip(), desc=ar[1].strip(),parent_id=ar[3],leftId=ar[4],rightId=ar[5])
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

    if sr.startswith('PMD'):
       brain = Brain(name=sr)
       brain.save()

       numSections = (len(os.listdir('/mnt/data001/MBAProcessingResults/PMD/'+sr))-1)/2

       sampleSectionNum = random.randrange(1,numSections)

       errorf.write(' sample section num ' + str(sampleSectionNum) + '\n')

       series_n = Series(desc=brain.name + ' Nissl Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu' ,lab_id=lab_m.id, labelMethod_id = lm_n.id, imageMethod_id = im_b.id, sectioningPlane_id=sp_s.id, numQCSections = numSections)
       series_n.save()

       series_f = Series(desc=brain.name + ' Flourescent Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu', lab_id=lab_m.id, labelMethod_id = lm_f.id, imageMethod_id = im_f.id, sectioningPlane_id=sp_s.id, numQCSections = numSections)
       series_f.save()

       series_ihc = Series(desc=brain.name + ' IHC Series', brain_id=brain.id, isRestricted=False, sectionThickness = 20, sectionThicknessUnit = 'mu' ,lab_id=lab_m.id, labelMethod_id = lm_ihc.id, imageMethod_id = im_b.id, sectioningPlane_id=sp_s.id, numQCSections = numSections)
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
                  injection = Injection(series_id = series_f.id, region_id = aralist[random.randrange(1,len(aralist)-1)].id, tracer_id = Tracer.objects.get(name=tn).id, volume=l.injvolume, volumeUnits=l.injvolunits, x_coord = l.xcoord, y_coord = l.ycoord, z_coord = l.zcoord)
                  injection.save()
               elif l.labelMethod.find("IHC") != -1:
                  injection = Injection(series_id = series_ihc.id, region_id = aralist[random.randrange(1,len(aralist)-1)].id, tracer_id = Tracer.objects.get(name=tn).id, volume=l.injvolume, volumeUnits=l.injvolunits, x_coord = l.xcoord, y_coord = l.ycoord, z_coord = l.zcoord)
                  injection.save()
               break
             except:
               errorf.write('Cannot save ' + sr + ' - ' + tn + '\n')

       sclist = os.listdir('/mnt/data001/MBAProcessingResults/PMD/'+sr)
       firstSection = True 
       for sc in sclist:
          if sc.startswith('meta'):
                scOrder = sc[sc.rfind("_")+1:sc.find(".txt")]

      #          sampleSection = False
      #          if sampleSectionNum == int(scOrder) :
      #             sampleSection = True
      #             errorf.write(" ******* sample section for " + sc + " is " + str(sampleSectionNum) + "\n")
                scName = sc[5:len(sc)-4]
                metaName = ''

                try:
                  metaName = '/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sc 
                  metaf=open(metaName)

                  metal = metaf.readline()

                  if metal.find(' N ') != -1:
                     section = Section(series_id=series_n.id, name=scName, sectionOrder=scOrder, pngPathHigh='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail.png',  pngPathLow='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail_smallest.png', jp2Path='/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2',jp2FileSize=os.path.getsize('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2'), jp2BitDepth=8, isSampleSection = firstSection)
                     section.save()

                  elif metal.find(' F ') != -1:
                     section = Section(series_id=series_f.id, name=scName, sectionOrder=scOrder, pngPathHigh='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail.png',  pngPathLow='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail_smallest.png', jp2Path='/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2',jp2FileSize=os.path.getsize('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2'), jp2BitDepth=16, isSampleSection = firstSection)
                     section.save()
                
                  elif metal.find(' IHC ') != -1:
                     section = Section(series_id=series_ihc.id, name=scName, sectionOrder=scOrder, pngPathHigh='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail.png',        pngPathLow='/mnt/data001/MBAProcessingResults/MaskOverview/PMD/'+sr+'/'+sr+'_'+scOrder+'_thumbnail_smallest.png', jp2Path='/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2',jp2FileSize=os.path.getsize('/mnt/data001/MBAProcessingResults/PMD/'+sr+'/'+sr+'_'+scOrder+'.jp2'), jp2BitDepth=8, isSampleSection = firstSection)
                     section.save()
                except:
                   errorf.write('File not found : ' + metaName + '\n')
                   #erirorf.write('File not found: \n')
                firstSection = False

