from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^seriesbrowser/$', 'seriesbrowser.views.index'),
    (r'^seriesbrowser/tree/$', 'seriesbrowser.views.tree'),
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
