from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import connection, transaction
from django.shortcuts import render_to_response
from seriesbrowser.models import Series

def index(request):
    sql = '''
    SELECT
        s.name,
        i.region,
        i.x,
        i.y,
        i.z
    FROM seriesbrowser_series s
    INNER JOIN seriesbrowser_injection_series si ON (s.id = si.series_id)
    INNER JOIN seriesbrowser_injection i ON (i.id = si.injection_id)
    '''

    where = '1'

    sort = request.GET.get('sort','name_asc')
    sort, dir = sort.split('_')

    field = 's.name'
    if sort == 'coord':
        field = 'i.x'
    if dir != 'asc' and dir != 'desc':
        dir = 'asc'
    order = ' '.join([field, dir])

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

    return render_to_response('seriesbrowser/index.html', {'series_page': series_page, 'sort' : sort, 'dir' : dir})