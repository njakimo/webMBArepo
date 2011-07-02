from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.shortcuts import render_to_response
from django import forms
from seriesbrowser.models import Tracer, Region, Series, Section, NearestSeries, Injection, Updater, SectionNote, LabelMethod, Brain
from settings import STATIC_DOC_ROOT
from django.http import HttpResponse, Http404
import json
import os
import re
from urllib import unquote
from urllib2 import urlopen, URLError
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch

from cStringIO import StringIO

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
         INNER JOIN seriesbrowser_section section ON (section.id = series.sampleSection_id)
         INNER JOIN seriesbrowser_labelmethod lm ON (series.labelMethod_id = lm.id AND lm.name <> 'Nissl')
         LEFT OUTER JOIN seriesbrowser_imagemethod im ON (series.imageMethod_id = im.id)
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
            sql = ' '.join([sql,' WHERE ',where])
    sql = ' '.join([sql,'ORDER BY',order])

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

def tree(request):
    try:
        root = Region.objects.get(pk=1)
        tree = root.generate_tree(2,request.user.is_authenticated())
    except ObjectDoesNotExist:
        tree = {}
    return render_to_response('seriesbrowser/tree.html', {
        'user' : request.user,
        'tree' : json.dumps(tree)})

def viewer(request, seriesId, sectionId=None):
    try:
        series = Series.objects.get(pk=seriesId)
        # preload the list of sections for generating filmstrip nav
        # TODO: this should order by y_coord descending
        sections = series.section_set.filter(isVisible=1).order_by('sectionOrder').all()
        nSections = len(sections)
        if not nSections:
            raise Http404
        # load specific section, otherwise use default
        if sectionId:
            try:
                section = series.section_set.get(pk=sectionId)
            except ObjectDoesNotExist:
                raise Http404
        else:
            section = series.sampleSection
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('seriesbrowser/viewer.html', {
        'sections' : sections,
        'section' : section,
        'nSections' : nSections
    })

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

def section(request, id):
    try:
        section = Section.objects.get(pk=id)
        series  = Series.objects.get(pk=section.series.id)
        inj  = Injection.objects.filter(series=series)
        if section.series.labelMethod.name != "Nissl":
            nissl = Series.objects.get(brain=section.series.brain,labelMethod=1)
            nisslID = nissl.id
        else:
            nisslID = 0
        
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
        atlasID = int((7.905 + section.y_coord)/13.25*131 + 130879)
        atlasID = min(131010,max(atlasID,130879))
        nSections = series.section_set.filter(isVisible=1).count()
    except ObjectDoesNotExist:
        section = None
    return render_to_response('seriesbrowser/ajax/section.html',{'section':section,'series':series, 'nslist':nslist, 'region':region, 'nisslID':nisslID, 'atlasID':atlasID,'nSections':nSections})

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
            curSec += 1
        closestSec.append(curSec)
        
    return render_to_response('seriesbrowser/injections.html', {
        'user' : request.user,
        'injection_list' : injection_list, # the injection records
        'tn_list' : tn_list, # the filenames of the atlas sections
        'yCoord' : secYCoord, # the y coordinates for each atlas section
        'closestSec' : closestSec}) # section to draw each injection on

def pdf(request, sectionId):
    section = None
    pdf = None
    image_url = None
    try:
        section = Section.objects.get(pk=sectionId)
        inj  = Injection.objects.filter(series=section.series.id)
        image_url = unquote(request.GET.get('image_url'))
        resp = urlopen(image_url)
        image = StringIO(resp.read())

        bapResp = urlopen('http://mbaimages.cshl.edu/wp-content/uploads/2011/01/mouse-header7.png');
        bapImg = StringIO(bapResp.read())

        buffer = StringIO()
        p = canvas.Canvas(buffer)
        p.setFont('Helvetica',10)
        p.setStrokeColor((0,0,0))
        p.drawString(0.375*inch,10.5*inch,'Series: ' + section.series.desc)
        if section.y_coord > 0:
            position = "Bregma +" + str(round(section.y_coord,2)) + "mm"
        else:
            position = "Bregma " + str(round(section.y_coord,2)) + "mm"
        p.drawString(0.375*inch,10.2*inch,'Approximate Section Location: ' + position)
        p.drawString(0.375*inch,10.0*inch,'Imaging Method: ' + section.series.imageMethod.name)
        p.drawString(0.375*inch,9.8*inch,'Label Method: ' + section.series.labelMethod.name)
        if inj:
            p.drawString(0.375*inch,9.6*inch,'Injection: '+inj[0].tracer.name + ' ('+str(inj[0].x_coord)+' mm, '+str(inj[0].y_coord)+' mm, '+str(inj[0].z_coord)+' mm)')
        p.drawString(0.375*inch,9.4*inch,'Color Range (RGB): ' + re.search('(?<=svc\.crange=)\d+-\d+,\d+-\d+,\d+-\d+', image_url).group(0) + ', Gamma: ' + re.search('(?<=svc\.gamma=)\d+\.*\d*', image_url).group(0))
        p.drawString(0.375*inch,9.2*inch,'Direct link to this section: http://mouse.brainarchitecture.org/seriesbrowser/viewer/'+str(section.series.id)+'/'+str(section.id))
        p.drawImage(ImageReader(image), 0.375*inch, 3.375*inch, 7.5*inch, 5.625*inch, preserveAspectRatio=True, anchor='nw')
        p.drawImage(ImageReader(bapImg),0.25*inch,0.25*inch,0.5*inch,0.5*inch,preserveAspectRatio=True,anchor='sw')

        p.setFont('Helvetica',14)
        p.drawString(0.75*inch,0.4*inch,'Brain Architecture Project (http://mouse.brainarchitecture.org)');
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
    except ObjectDoesNotExist:
        raise Http404
    except URLError:
        raise Http404

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=section'+str(section.name)+'.pdf'
    response.write(pdf)
    return response

def metadata(request):
    response = None
    try:
        response = urlopen('http://mouse.brainarchitecture.org/webapps/adore-djatoka/resolver?' + request.GET.urlencode())
    except URLError:
        raise Http404
    return HttpResponse(response)
