from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.shortcuts import render_to_response
from django import forms
from seriesbrowser.models import Tracer, Region, Series, Section, NearestSeries, Injection, Updater, SectionNote, LabelMethod, Brain
from settings import STATIC_DOC_ROOT
import json, os
import datetime

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
            series.id as seriesId     
         FROM seriesbrowser_series series     
         LEFT OUTER JOIN seriesbrowser_injection injection ON (injection.series_id = series.id) 
         LEFT OUTER JOIN seriesbrowser_tracer tracer ON (injection.tracer_id = tracer.id) 
         LEFT OUTER  JOIN seriesbrowser_region region ON (injection.region_id = region.id) 
         INNER JOIN seriesbrowser_section section ON (section.series_id = series.id)     WHERE section.isSampleSection = 1
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
        field = 'x_coord'
        extra = ' '.join([',y_coord',dir,',z_coord',dir])
    elif sort == 'coordy':
        field = 'y_coord'
        extra = ' '.join([',x_coord',dir,',z_coord',dir])
    elif sort == 'coordz':
        field = 'z_coord'
        extra = ' '.join([',x_coord',dir,',y_coord',dir])
    elif sort == 'region':
        field = 'region.code'
    elif sort == 'tracer':
        field = 'tracer.name'
    order = ' '.join([field, dir, extra])

    sql = ' '.join([sql,' AND ',where,'ORDER BY',order])

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
        'form'        : form})
def tree(request):
    try:
        root = Region.objects.get(pk=1)
        tree = root.generate_tree(2,request.user.is_authenticated())
    except ObjectDoesNotExist:
        tree = {}
    return render_to_response('seriesbrowser/tree.html', {
        'user' : request.user,
        'tree' : json.dumps(tree)})

def viewer(request):
    try:
        series_id = int(request.GET.get('seriesId','0'))
    except ValueError:
        series_id = 0
    try:
        series = Series.objects.get(pk=series_id)
        sections = series.section_set.order_by('sectionOrder').all()
        section_id = 0
        try:
           section_id =  int(request.GET.get('sectionId','0'))
        except:
           pass
        if section_id != 0:  
           section = Section.objects.get(pk = section_id)
        else:
           section = sections[0]     
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
        section = None
    return render_to_response('seriesbrowser/viewer.html',{'sections' : sections, 'section': section, 'series':series, 'nslist':nslist, 'region':region})

def allSections(request):
    try:
        series_id = int(request.GET.get('seriesId','0'))
    except ValueError:
        series_id = 0
    try:
        series = Series.objects.get(pk=series_id)
        sections = series.section_set.order_by('sectionOrder').all()
        section = sections[0]
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
        section = None
    return render_to_response('seriesbrowser/allSections.html',{'sections' : sections, 'section': section, 'series':series, 'nslist':nslist, 'region':region})

def section(request,id):
    try:
        section = Section.objects.get(pk=id)
        series  = Series.objects.get(pk=section.series.id)
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
        section = None
    return render_to_response('seriesbrowser/ajax/section.html',{'section':section,'series':series, 'nslist':nslist, 'region':region})

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

def showNissl(request,id):
    try:
        series_id = int(request.GET.get('seriesId','0'))
        series  = Series.objects.get(pk=series_id)
        sections = Section.objects.filter(series = series)
        section = sections[0]
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
        scFinalList = []
        scList = []
        if l_method.name != 'Nissl':
            slist = Series.objects.filter(brain=series.brain)
            for sr in slist:
                if sr.id != series.id:
                    l_m1 = LabelMethod.objects.get(pk=sr.labelMethod_id)
                    if l_m1.name == 'Nissl':
                       sclist = Section.objects.filter(series=sr)

        scOriginallist  = Section.objects.filter(series=series)
        scFinal11List = sorted(scList + sc1List)
    except ObjectDoesNotExist:
        section = None
    return render_to_response('seriesbrowser/viewer.html',{'sections':scFinalList, 'section':section,'series':series, 'nslist':nslist, 'region':region})

def injections(request):
    # 'View 2' - show injection locations graphically in atlas context

    injection_list = Injection.objects.order_by('-y_coord')
    tnDir = STATIC_DOC_ROOT + '/img/jpgSections/tn'
#    tn_list = os.listdir('X:/MBAPortal/njakimo-webMBArepo-80d5844/static/img/jpgSections/TN')
    tn_list = os.listdir(tnDir)
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
        while secYCoord[curSec]>y.y_coord:
            curSec = curSec + 1
        closestSec.append(curSec)
        
    return render_to_response('seriesbrowser/injections.html', {
        'user' : request.user,
        'injection_list' : injection_list, # the injection records
        'tn_list' : tn_list, # the filenames of the atlas sections
        'yCoord' : secYCoord, # the y coordinates for each atlas section
        'closestSec' : closestSec}) # section to draw each injection on
