from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://mbaimages.cshl.edu/?page_id=2'}),
    (r'^seriesbrowser/$', 'seriesbrowser.views.index'),
    (r'^seriesbrowser/aux/$','seriesbrowser.views.aux'),
    (r'^seriesbrowser/injections/$', 'seriesbrowser.views.injections'),
    (r'^seriesbrowser/tree/$', 'seriesbrowser.views.tree'),
    url(r'^seriesbrowser/viewer/(?P<seriesId>\d+)/$', 'seriesbrowser.views.viewer', name='series_viewer'),
    url(r'^seriesbrowser/viewer/(?P<seriesId>\d+)/(?P<sectionId>\d+)/$', 'seriesbrowser.views.viewer', name='section_viewer'),
    (r'^seriesbrowser/gallery/(?P<seriesId>\d+)/$', 'seriesbrowser.views.gallery'),
    (r'^seriesbrowser/gallery/(?P<seriesId>\d+)/(?P<showNissl>\d+)$', 'seriesbrowser.views.gallery'),
    (r'^seriesbrowser/showComments/(?P<seriesId>\d+)/$', 'seriesbrowser.views.showComments'),
    (r'^seriesbrowser/ajax/section/(?P<id>\d+)/$', 'seriesbrowser.views.section'),
    (r'^seriesbrowser/pdf/(?P<sectionId>\d+)/$', 'seriesbrowser.views.pdf'),
   (r'^seriesbrowser/ajax/section/(?P<id>\d+)/(?P<comment>.*)$', 'seriesbrowser.views.addNote'),
    (r'^seriesbrowser/metadata/$', 'seriesbrowser.views.metadata'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    # Example:
    # (r'^webMBA/', include('webMBA.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^register/', 'seriesbrowser.views.register'),
    (r'^accounts/', include('registration.backends.default.urls')),
)
