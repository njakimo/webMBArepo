from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import connection, transaction
from django.shortcuts import render_to_response
from seriesbrowser.models import Series, Tracer

from django import forms

class FilterForm(forms.Form):
    filter = forms.ModelChoiceField(Tracer.objects.order_by('name').all())

def index(request):
    sql = '''
    
    SELECT
        series.desc as seriesDesc,
        region.code as regionCode,
        region.desc as regionDesc,
        injection.x_coord as xCoord,
        injection.y_coord as yCoord,
        injection.z_coord as zCoord,
        injection.volume as volume,
        injection.volumeUnits as volumeUnits,
        tracer.name as tracerName
    FROM seriesbrowser_series series
    INNER JOIN seriesbrowser_section section ON (section.series_id = series.id)
    LEFT OUTER JOIN seriesbrowser_injection injection ON (injection.section_id = section.id)
    INNER JOIN seriesbrowser_tracer tracer ON (tracer.injection_id = injection.id)
    INNER JOIN seriesbrowser_region region ON (region.id = injection.region_id)
    
    '''

    try:
        filter = int(request.GET.get('filter','0'))
    except ValueError:
        filter = 0

    where = '1'
    if filter > 0:
        where = ' '.join(['t.id =',str(filter)])

    sort = request.GET.get('sort','name_asc')
    sort, dir = sort.split('_')

    if dir != 'asc' and dir != 'desc':
        dir = 'asc'

    field = 'seriesDesc'
    extra = ''
    if sort == 'coordx':
        field = 'xCoord'
        extra = ' '.join([',i.y',dir,',i.z',dir])
    elif sort == 'coordy':
        field = 'yCoord'
        extra = ' '.join([',i.x',dir,',i.z',dir])
    elif sort == 'coordz':
        field = 'zCoord'
        extra = ' '.join([',i.x',dir,',i.y',dir])
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

    form = FilterForm()

    return render_to_response('seriesbrowser/index.html', {
        'series_page': series_page,
        'sort'       : sort,
        'dir'        : dir,
        'filter'     : request.GET.get('filter',None),
        'form'       : form})
