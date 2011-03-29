from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import connection
from django.shortcuts import render_to_response
from django import forms
from seriesbrowser.models import Tracer, Region

import json

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
        series.numQCSections as qcSections
    FROM seriesbrowser_series series
    LEFT OUTER JOIN seriesbrowser_injection injection ON (injection.series_id = series.id)
    INNER JOIN seriesbrowser_tracer tracer ON (injection.tracer_id = tracer.id)
    INNER JOIN seriesbrowser_region region ON (injection.region_id = region.id)
    
    '''

    try:
        tracer_filter = int(request.GET.get('tracer_filter','0'))
    except ValueError:
        tracer_filter = 0

    try:
        region_filter = int(request.GET.get('region_filter','0'))
    except ValueError:
        region_filter = 0

    where = '1'
    if tracer_filter > 0:
        where = ' '.join(['tracer.id =',str(tracer_filter)])
    if region_filter > 0:
        region = Region.objects.get(pk=region_filter)
        if where == '1':
            where = ' '.join(['injection.region_id IN (', ','.join(map(str,region.descendant_ids())), ')'])
        else:
            where = ' '.join([where,'AND injection.region_id IN (', ','.join(map(str,region.descendant_ids())), ')'])


    sort = request.GET.get('sort','name_asc')
    sort, dir = sort.split('_')

    if dir != 'asc' and dir != 'desc':
        dir = 'asc'

    field = 'seriesDesc'
    extra = ''
    if sort == 'coordx':
        field = 'xCoord'
        extra = ' '.join([',yCoord',dir,',zCoord',dir])
    elif sort == 'coordy':
        field = 'yCoord'
        extra = ' '.join([',xCoord',dir,',zCoord',dir])
    elif sort == 'coordz':
        field = 'zCoord'
        extra = ' '.join([',xCoord',dir,',yCoord',dir])
    elif sort == 'region':
        field = 'regionCode'
    elif sort == 'tracer':
        field = 'tracerName'
    order = ' '.join([field, dir, extra])

    sql = ' '.join([sql,'WHERE',where,'ORDER BY',order])

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
        'series_page' : series_page,
        'sort'        : sort,
        'dir'         : dir,
        'filters'     : filters,
        'form'        : form})

def tree(request):
    root = Region.objects.get(pk=1)
    tree = json.dumps(root.generate_tree(2))
    return render_to_response('seriesbrowser/tree.html', {'tree' : tree})