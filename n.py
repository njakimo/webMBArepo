import django
import seriesbrowser
import os
import random
import math

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
from seriesbrowser.models import NearestSeries
from django.db import connection

distf = open('../csvfiles/distance.txt', 'w')

#load data from ARA
slist = Series.objects.all()

for s in slist:
    #inj = Injection.objects.get(series__id = s.id)

    inj = Injection.objects.filter(series = s)
    i_sid = 0
    x_coord = 0
    y_coord = 0
    z_coord = 0

    for i in inj:
        x_coord = i.x_coord
        y_coord = i.y_coord
        z_coord = i.z_coord
        i_sid = i.series_id
        break

   # si = Series.objects.get(pk=int(i_sid)) 
    
    ilist = Injection.objects.all()

    for i in ilist:
        if i.series_id != i_sid:
           d = math.sqrt((i.x_coord-x_coord)*(i.x_coord-x_coord)+(i.y_coord-y_coord)*(i.y_coord-y_coord)+(i.z_coord-z_coord)*(i.z_coord-z_coord))
           distf.write("Distance between " + s.desc + " and " + str(i.series_id) + " = " + str(d) + "\n") 
           if d <= 3 :
              nn = NearestSeries(distance=str(d), series_id = i.series_id)
              distf.write("In save " + str(d) + " series id " + str(i.series_id) +  "\n") 
              nn.save()
   
 #distf.write(s.desc + '\n')
