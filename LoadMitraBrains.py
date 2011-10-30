import django
import seriesbrowser
import os
import random
import re
import pickle
import sys
import glob

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

from UpdateLimsLookup import Mouse
series2limsDict = pickle.load(open("../pckfiles/series2limsDict.p", 'rb'))

ara25um = pickle.load(open("../pckfiles/ara25um.pck"))
orgn = {'x':228, 'y':221, 'z':36}

for brainPath  in glob.glob("/brainimg//MouseBrain*"):
	brainName = brainPath[brainPath.rfind("/")+1:len(brainPath)]

	try:
		brain = Brain(name=brainName)
		brain.save()
		print 'Adding ' + brainName	
	except:
		print 'Skipping ' + brainName
		continue

	section2yDict = {}
	section2labelDict = {}
	labelBOOLDict = {}
	with open('/brainimg/' + brainName + '/ImageLookup.txt') as f:
		for line in f:
			m = re.match(r"(Section.*)\:\s+(-?\d+.\d+)\s+(N|IHC|F)", line)
			section2yDict[m.group(1)] = m.group(2)
			section2labelDict[m.group(1)] = m.group(3)
			labelBOOLDict[m.group(3)] = 1

	idSeries = -1
	label2fullDict = {'N':'Nissl', 'IHC':'IHC', 'F':'Fluorescent'}
	label2fieldDict = {'N':'Brightfield', 'IHC':'Brightfield', 'F':'Fluorescent'}
	for label in ('N', 'IHC', 'F'):
		if label in labelBOOLDict:
			series = Series(desc = brain.name + ' ' + label2fullDict[label], 
					brain_id = brain.id, sectionThickness = 20,
					lab_id = Laboratory.objects.get(name='Mitra').id, 
					labelMethod_id = LabelMethod.objects.get(name=label2fullDict[label]).id, 
					imageMethod_id = ImageMethod.objects.get(name=label2fieldDict[label]).id,
					sectioningPlane_id = SectioningPlane.objects.get(desc='Coronal').id)
			series.save()
			if label == 'IHC' or label == 'F':
				idSeries = series.id

	mouse = series2limsDict[brainName]
	tn = mouse.tracer
	try:
		tracer = Tracer(name=tn)
		tracer.save()
	except:
		pass

	try:
		if not idSeries == -1:
			injectionID = ara25um[orgn['x']+round(float(mouse.xcoord)*1000/25),
					orgn['z']+round(float(mouse.zcoord)*1000/25),
					orgn['y']-round(float(mouse.ycoord)*1000/25)]
        		injection = Injection(series_id = idSeries, region_id = injectionID, 
					tracer_id = Tracer.objects.get(name=tn).id,
                                	volume = mouse.injvolume, volumeUnits=mouse.injvolunits,
                                	x_coord = mouse.xcoord, y_coord = mouse.ycoord, z_coord = mouse.zcoord)
	        	injection.save()
	except:
		continue

	dist2injDict = {'N':100, 'IHC':100, 'F':100}
	label2uintDict = {'N':8, 'IHC':8, 'F':16}
	for sectionName in section2labelDict:
		if os.path.exists('/brainimg/' + brainName + '/' + sectionName + '.jp2'):
			label = section2labelDict[sectionName]
			series = Series.objects.get(desc=brain.name + ' ' + label2fullDict[label])
			series.numQCSections += 1
			series.save()
			section = Section(series_id = series.id, name = sectionName, 
						sectionOrder = sectionName[sectionName.rfind("_")+1:len(sectionName)],
						pngPathLow = '/brainimg/' + brainName + '/' + sectionName + '.jpg', 
						jp2Path = '/brainimg/' + brainName + '/' + sectionName + '.jp2', 
						jp2FileSize = os.path.getsize('/brainimg/'+brainName+'/'+sectionName+'.jp2'),
						jp2BitDepth = label2uintDict[label], y_coord = section2yDict[sectionName])
			section.save()
			dataresolver = DataResolver(section_id = section.id, identifier = 'MouseBrain/'+str(section.id), 
							imageFile='/brainimg/'+brainName+'/'+sectionName+'.jp2')
			dataresolver.save()

			try:
				dist2injSec = abs(float(section2yDict[sectionName])-float(mouse.ycoord))
				if dist2injSec < dist2injDict[label]:
					dist2injDict[label] = dist2injSec
					series.sampleSection_id = section.id
			except:
				series.sampleSection_id = section.id	
		
			series.save()
