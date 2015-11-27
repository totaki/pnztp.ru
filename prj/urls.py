from django.conf.urls import patterns, include, url
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from external_site.views import (
  RootView, AnnouncesView, NewsListView, NewsDetailView, NewsPartnersView,
  TourView, CaptchaView, RezidentsView
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', url(r'^$', RootView.as_view(),),
                          url(r'^announces/$', AnnouncesView.as_view(),),
                          url(r'^news/page/(\d{1,2})/$', NewsListView.as_view(),),
                          url(r'^news/(\d{1,4})/$', NewsDetailView.as_view(),),
                          url(r'^news/partners/$', cache_page(60 * 15)(NewsPartnersView.as_view()),),
                          url(r'^tour/$', csrf_exempt(TourView.as_view()),),
                          url(r'^captcha/$', csrf_exempt(CaptchaView.as_view()),),
                          url(r'^rezidents/$', RezidentsView.as_view(),),
)

urlpatterns += patterns(url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),)

urlpatterns += (patterns(url(r'^admin/', include(admin.site.urls)),))
urlpatterns += staticfiles_urlpatterns()
