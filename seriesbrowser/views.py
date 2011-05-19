from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.shortcuts import render_to_response
from django import forms
from seriesbrowser.models import Tracer, Region, Series, Section, NearestSeries, Injection, Updater, SectionNote, LabelMethod, Brain
from settings import STATIC_DOC_ROOT
from django.http import HttpResponse
from PIL import Image
import json, os
import datetime
import reportlab

class FilterForm(forms.Form):
    tracer_filter = forms.ModelChoiceField(Tracer.objects.order_by('name').all())
    region_filter = forms.ModelChoiceField(Region.objects.order_by('code').all())

def index(request):
    sql = '''
         SELECT
            series.desc as seriesDesc,
            region.code as regionCode,  
            injection.x_coord as xCoord,  
            injection.y_coord as yCoord, 
            injection.z_coord as zCoord,   
            tracer.name as tracerName, 
            series.numQCSections as qcSections,
            section.pngPathLow as imagePath,     
            series.id as seriesId,
            region.desc as regionDesc,       
            im.name as imageMethod       
         FROM seriesbrowser_series series     
         LEFT OUTER JOIN seriesbrowser_injection injection ON (injection.series_id = series.id) 
         LEFT OUTER JOIN seriesbrowser_tracer tracer ON (injection.tracer_id = tracer.id) 
         LEFT OUTER  JOIN seriesbrowser_region region ON (injection.region_id = region.id) 
         INNER JOIN seriesbrowser_section section ON (section.series_id = series.id)  
         LEFT OUTER JOIN seriesbrowser_labelmethod lm ON (series.labelMethod_id = lm.id)  
         LEFT OUTER JOIN seriesbrowser_imagemethod im ON (series.imageMethod_id = im.id)  
         WHERE section.isSampleSection = 1
         AND lm.name <> 'Nissl'        
    '''

    try:
        tracer_filter = int(request.GET.get('tracer_filter','0'))
    except ValueError:
        tracer_filter = 0

    try:
        region_filter = int(request.GET.get('region_filter','0'))
    except ValueError:
        region_filter = 0

#    where = '1'
    where = ''
    if tracer_filter > 0:
        where = ' '.join(['tracer.id =',str(tracer_filter)])
    if region_filter > 0:
        region = Region.objects.get(pk=region_filter)
        if where == '':
            where = ' '.join(['injection.region_id IN (', ','.join(map(str,region.descendant_ids())), ')'])
        else:
            where = ' '.join([where,'AND injection.region_id IN (', ','.join(map(str,region.descendant_ids())), ')'])

    if not request.user.is_authenticated():
        if where == '':
           where += ' series.isRestricted = 0'
        else:
           where += ' AND series.isRestricted = 0'


    sort = request.GET.get('sort','name_asc')
    sort, dir = sort.split('_')

    if dir != 'asc' and dir != 'desc':
        dir = 'asc'

    field = 'series.desc'
    extra = ''
    if sort == 'coordx':
        field = 'injection.x_coord'
        extra = ' '.join([',injection.y_coord',dir,',injection.z_coord',dir])
    elif sort == 'coordy':
        field = 'injection.y_coord'
        extra = ' '.join([',injection.x_coord',dir,',injection.z_coord',dir])
    elif sort == 'coordz':
        field = 'injection.z_coord'
        extra = ' '.join([',injection.x_coord',dir,',injection.y_coord',dir])
    elif sort == 'region':
        field = 'region.code'
    elif sort == 'tracer':
        field = 'tracer.name'
    order = ' '.join([field, dir, extra])
    if where != '':
            sql = ' '.join([sql,' AND ',where])
    sql = ' '.join([sql,'ORDER BY',order])
#    sql1 = ' '.join([sql,' AND ',where,'ORDER BY',order])
    cursor = connection.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    paginator = Paginator(rs, 25)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        series_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        series_page = paginator.page(paginator.num_pages)
    form = FilterForm(initial={'tracer_filter' : tracer_filter, 'region_filter' : region_filter})
    filters = '&'.join(["tracer_filter=" + str(tracer_filter),"region_filter=" + str(region_filter)])
    return render_to_response('seriesbrowser/index.html', {
        'user'        : request.user,
        'series_page' : series_page,
        'sort'        : sort,
        'dir'         : dir,
        'filters'     : filters,
        'form'        : form,})
#        'sql'           :sql,})

def tree(request):
    try:
        root = Region.objects.get(pk=1)
        tree = root.generate_tree(2,request.user.is_authenticated())
    except ObjectDoesNotExist:
        tree = {}
    return render_to_response('seriesbrowser/tree.html', {
        'user' : request.user,
        'tree' : json.dumps(tree)})

def sectionViewer(request, seriesId, sectionId):
    try:
        series = Series.objects.get(pk=seriesId)
        # in case the user comes in by clicking on a Nissl series, show the corresponding IHC or flourescent series
        lm = LabelMethod.objects.get(pk=series.labelMethod_id)
        if lm.name == 'Nissl':
           slist = Series.objects.filter(brain=series.brain)
           for sr in slist:
                if sr.id != series.id:
                    lm1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if lm1.name != 'Nissl':
                        series = sr
                        break
        sections = series.section_set.order_by('sectionOrder').all()
        numSections = len(sections)
        screen = '1'
        showNissl = '0'
        if sectionId != 0: 
            section = Section.objects.get(pk=sectionId)
        else: 
            section = sections[0]    
            section = Section.objects.get(pk=1)    
        inj  = Injection.objects.filter(series=series)
        region = ''         
        for i in inj:
           region  = Region.objects.get(pk=i.region.id)
           break
        ns = NearestSeries.objects.filter(series=series)
        nslist = []
        for n in ns:
           s = Series.objects.get(pk=n.nearestSeriesId)
           nslist.append(s)
           if len(nslist) >= 5:
              break
    except ObjectDoesNotExist:
        sections = None
    return render_to_response('seriesbrowser/viewer.html',{'sections' : sections, 'section': section, 'series':series, 'nslist':nslist, 'region':region, 'numSections':numSections, 'screen':screen, 'showNissl':showNissl})

def viewer(request, seriesId):
    try:
        series = Series.objects.get(pk=seriesId)
        # in case the user comes in by clicking on a Nissl series, show the corresponding IHC or flourescent series
        lm = LabelMethod.objects.get(pk=series.labelMethod_id)
        if lm.name == 'Nissl':
           slist = Series.objects.filter(brain=series.brain)
           for sr in slist:
                if sr.id != series.id:
                    lm1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if lm1.name != 'Nissl':
                        series = sr
                        break
        sections = series.section_set.order_by('sectionOrder').all()
        numSections = len(sections)
        section = sections[0]    
        inj  = Injection.objects.filter(series=series)
        region = ''         
        screen = '1'
        showNissl = '0'
        for i in inj:
           region  = Region.objects.get(pk=i.region.id)
           break
        ns = NearestSeries.objects.filter(series=series)
        nslist = []
        for n in ns:
           s = Series.objects.get(pk=n.nearestSeriesId)
           nslist.append(s)
           if len(nslist) >= 5:
              break
    except ObjectDoesNotExist:
        sections = None
    return render_to_response('seriesbrowser/viewer.html',{'sections' : sections, 'section': section, 'series':series, 'nslist':nslist, 'region':region, 'numSections':numSections, 'screen':screen, 'showNissl':showNissl})

def gallery(request, seriesId):
    try:
        series = Series.objects.get(pk=seriesId)
        sections = series.section_set.order_by('sectionOrder').all()
        section = sections[0]
        numSections = len(sections)
        inj  = Injection.objects.filter(series=series)
        region = ''         
        screen = '0'
        showNissl = '0'
        for i in inj:
           region  = Region.objects.get(pk=i.region.id)
           break
        ns = NearestSeries.objects.filter(series=series)
        nslist = []
        for n in ns:
           s = Series.objects.get(pk=n.nearestSeriesId)
           nslist.append(s)
           if len(nslist) >= 5:
              break
    except ObjectDoesNotExist:
        sections = None
        section = None
    return render_to_response('seriesbrowser/gallery.html',{'sections' : sections, 'section': section, 'series':series, 'nslist':nslist, 'region':region, 'numSections':numSections, 'screen':screen, 'showNissl':showNissl})

def section(request,id, showNissl, screen):
    try:
        section = Section.objects.get(pk=id)
        series  = Series.objects.get(pk=section.series.id)
        # if this is a Nissl series, get the corresponding flourescent or IHC series and set that as the series
        lm = LabelMethod.objects.get(pk=series.labelMethod_id)
        try:
          if lm.name == 'Nissl':
             slist = Series.objects.filter(brain=series.brain)
             for sr in slist:
                if sr.id != series.id:
                    lm1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if lm1.name != 'Nissl':
                        series = sr
                        break
        except:
          pass
        inj  = Injection.objects.filter(series=series)
        region = ''         
        showNissl='0'
        for i in inj:
           region  = Region.objects.get(pk=i.region.id)
           break
        ns = NearestSeries.objects.filter(series=series)
        nslist = []
        for n in ns:
           s = Series.objects.get(pk=n.nearestSeriesId)
           nslist.append(s)
           if len(nslist) >= 5:
              break
    except ObjectDoesNotExist:
        section = None
    return render_to_response('seriesbrowser/ajax/section.html',{'section':section,'series':series, 'nslist':nslist, 'region':region, 'showNissl':showNissl, 'screen':screen})

#def addNote(request,id):
#    try:
#        section = Section.objects.get(pk=id)
#        series  = Series.objects.get(pk=section.series.id)
#        inj  = Injection.objects.filter(series=series)
#        region = ''         
#        for i in inj:
#           region  = Region.objects.get(pk=i.region.id)
#           break
#        ns = NearestSeries.objects.filter(series=series)
#        nslist = []
#        for n in ns:
#           s = Series.objects.get(pk=n.nearestSeriesId)
#           nslist.append(s)
#           if len(nslist) >= 5:
#              break
    #   add notes and comment
#        u = Updater.objects.get(pk=1)    
#        sc = request.GET.get('score','')
#        nt = request.GET.get('note','')
#        sn = request.GET.get('showNissl','')
#        sNote = SectionNote(section_id=section.id, updater_id = u.id, score = sc , comment = nt, write_date = datetime.datetime.now())        
#        sNote.save() 
#    except ObjectDoesNotExist:
#        section = None
#    return render_to_response('seriesbrowser/ajax/section.html',{'section':section,'series':series, 'nslist':nslist, 'region':region,'sectionNote':sNote, 'showNissl':sn})

def showNissl(request, id, showNissl, screen):
    series  = Series.objects.get(pk=id)
    sections = series.section_set.order_by('sectionOrder').all()
    section = sections[0]
    if screen == '0':
        forward = "gallery"
    elif screen == '1': 
        forward = "viewer"
    inj  = Injection.objects.filter(series=series)
    region = ''         
    for i in inj:
        region  = Region.objects.get(pk=i.region.id)
        break
    ns = NearestSeries.objects.filter(series=series)
    nslist = []
    for n in ns:
        s = Series.objects.get(pk=n.nearestSeriesId)
        nslist.append(s)
        if len(nslist) >= 5:
           break
    l_method = LabelMethod.objects.get(pk=series.labelMethod_id)
    scFinalList = sections
    if showNissl == '1':
      scList = []
      try:
        if l_method.name != 'Nissl':
            slist = Series.objects.filter(brain=series.brain)
            for sr in slist:
                if sr.id != series.id:
                    l_m1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if l_m1.name == 'Nissl':
                        scList = Section.objects.filter(series=sr)
                        finalList = list(scList)+list(sections)
                        scFinalList =  sorted(finalList, key=lambda x: x.sectionOrder )
                        break
      except:
        pass
    numSections = len(scFinalList)
    return render_to_response('seriesbrowser/' + forward + '.html',{'sections':scFinalList, 'section':section,'series':series, 'nslist':nslist, 'region':region, 'numSections':numSections, 'screen':screen, 'showNissl':showNissl})

def showOnlyNissl(request, id, sectionId):
    series  = Series.objects.get(pk=id)
    sections = series.section_set.order_by('sectionOrder').all()
    section  = Section.objects.get(pk=sectionId)
    inj  = Injection.objects.filter(series=series)
    region = ''         
    for i in inj:
        region  = Region.objects.get(pk=i.region.id)
        break
    ns = NearestSeries.objects.filter(series=series)
    nslist = []
    for n in ns:
        s = Series.objects.get(pk=n.nearestSeriesId)
        nslist.append(s)
        if len(nslist) >= 5:
           break
    l_method = LabelMethod.objects.get(pk=series.labelMethod_id)
    scList = []
    try:
        if l_method.name != 'Nissl':
            slist = Series.objects.filter(brain=series.brain)
            for sr in slist:
                if sr.id != series.id:
                    l_m1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if l_m1.name == 'Nissl':
                        scList = Section.objects.filter(series=sr)
                        break
    except:
        pass
    numSections = len(scList)
    screen = "2"
    showNissl = "2"
    return render_to_response('seriesbrowser/viewer.html',{'sections':scList, 'section':section,'series':series, 'nslist':nslist, 'region':region, 'numSections':numSections, 'showNissl':showNissl,'screen':screen})
   
def injections(request):
    # 'View 2' - show injection locations graphically in atlas context
    injection_list = Injection.objects.order_by('-y_coord')
    tnDir = STATIC_DOC_ROOT + '/img/jpgSections/tn'
#    tn_list = os.listdir('X:/MBAPortal/njakimo-webMBArepo-80d5844/static/img/jpgSections/TN')
    tn_list = os.listdir(tnDir)
    tn_list.sort()  
    nSections = len(tn_list)
    secYCoord = [] 
    for i in range(nSections):
        # Map each section linearly to a y coordinate value (approximate)
        temp = 5.435 - 13.25 * i / (nSections-1)
        secYCoord.append(temp)
    # Find the closest section for each injection - it will be drawn
    # on that section in the application
    curSec = 0
    closestSec = []
    for y in injection_list:
        while secYCoord[curSec]>float(y.y_coord):
            curSec = curSec + 1
        closestSec.append(curSec)
        
    return render_to_response('seriesbrowser/injections.html', {
        'user' : request.user,
        'injection_list' : injection_list, # the injection records
        'tn_list' : tn_list, # the filenames of the atlas sections
        'yCoord' : secYCoord, # the y coordinates for each atlas section
        'closestSec' : closestSec}) # section to draw each injection on

def downloadPDF(request, id):
     response = HttpResponse(mimetype='application/pdf')
     try:
        section = Section.objects.get(pk=id)
        series  = Series.objects.get(pk=section.series.id)
        response['Content-Disposition'] = 'attachment; filename=section'+str(section.name)+'.pdf'
        buffer = StringIO()
        # Create the PDF object, using the buffer 
        p = canvas.Canvas(buffer)
        # Draw things on the PDF. Here's where the PDF generation happens.
        p.drawString(100, 100, section.name)
        im = Image.open(section.pngPathLow)
        p.drawImage(self, im, 100,100, width=90,height=120,mask=None) 
        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()
        # Get the value of the StringIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
     except:
       pass
     return response

