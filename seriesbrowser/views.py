from django.shortcuts import render_to_response
from seriesbrowser.models import Series

def index(request):
    series_list = Series.objects.all().order_by('name')
    return render_to_response('seriesbrowser/index.html', {'series_list': series_list})
