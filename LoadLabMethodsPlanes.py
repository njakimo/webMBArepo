import django
import seriesbrowser
import os
import random
import re
import pickle
import sys

from seriesbrowser.models import Laboratory
from seriesbrowser.models import LabelMethod
from seriesbrowser.models import ImageMethod
from seriesbrowser.models import SectioningPlane

lab = Laboratory(name='Mitra')
lab.save()

for plane in ('Sagittal', 'Coronal', 'Tranverse'):
	sp = SectioningPlane(desc=plane)
	sp.save()

for label in ('Nissl', 'Fluorescent', 'IHC'):
	lm = LabelMethod(name=label)
	lm.save()

for field in ('Brightfield', 'Fluorescent'):
	im = ImageMethod(name=field)
	im.save()
