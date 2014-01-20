from django.conf.urls import patterns, include, url
from django.views.generic import ListView

from django.contrib import admin
admin.autodiscover()

from presentations.models import Presentation


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Presentation), name='presentations'),
    url(r'^admin/', include(admin.site.urls)),
)
