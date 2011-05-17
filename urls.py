from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://mbaimages.cshl.edu/?page_id=2'}),
    (r'^seriesbrowser/$', 'seriesbrowser.views.index'),
    (r'^seriesbrowser/injections/$', 'seriesbrowser.views.injections'),
    (r'^seriesbrowser/tree/$', 'seriesbrowser.views.tree'),
    (r'^seriesbrowser/viewer/(?P<seriesId>\d+)/(?P<sectionId>\d+)/$', 'seriesbrowser.views.sectionViewer'),
    (r'^seriesbrowser/viewer/(?P<seriesId>\d+)/$', 'seriesbrowser.views.viewer'),
    (r'^seriesbrowser/gallery/(?P<seriesId>\d+)/$', 'seriesbrowser.views.gallery'),
    (r'^seriesbrowser/ajax/section/(?P<id>\d+)/(?P<showNissl>\d+)/(?P<screen>\d+)/$', 'seriesbrowser.views.section'),
    (r'^seriesbrowser/showNissl/(?P<id>\d+)/(?P<showNissl>\d+)/(?P<screen>\d+)/$', 'seriesbrowser.views.showNissl'),
    (r'^seriesbrowser/showOnlyNissl/(?P<id>\d+)/$', 'seriesbrowser.views.showOnlyNissl'),
    (r'^seriesbrowser/login/$', 'django.contrib.auth.views.login', {'template_name': 'seriesbrowser/login.html'}),
    (r'^seriesbrowser/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/seriesbrowser/'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    # Example:
    # (r'^webMBA/', include('webMBA.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
