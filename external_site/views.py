# -*- coding:utf-8 -*-
import json
from random import randint as random_int
from datetime import date
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from external_site import partners
from external_site.captcha import get_yandex_captcha
from external_site.models import (
  News, Announce, Rezidents, Infrastructure, GalleryImage, GovermentOrg, return_tmb_path
)
from external_site.utils import tour


ANNOUNCES = 'announces'
REZIDENTS = 'rezidents'
NEWS = 'news'
NEWS_PER_PAGE = 12
PAGE_PER_PAGE = 9


def _rowed_list(list_, per_list):
    num_rows = len(list_)/per_list + int(bool(len(list_)%per_list))
    for i in range(0, num_rows):
      yield (j for j in list_[i*per_list:(i+1)*per_list])
      

class JsonView(TemplateView):
    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(
            self.convert_context_to_json(self.func()),
            content_type='application/json',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        return json.dumps(context)

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class RootView(TemplateView):
    template_name = 'root.htm'

    def get_context_data(self, **kwargs):
        context = super(RootView, self).get_context_data(**kwargs)
        for i,j in ([NEWS, News.objects.all()[:3]],
                    [ANNOUNCES, Announce.get_and_check()]):
            context[i] = j
        context[ANNOUNCES + '_count'] = range(0, len(context[ANNOUNCES]))
        return context


class AnnouncesView(TemplateView):
    template_name = 'announces.htm'

    def get_context_data(self, **kwargs):
        context = super(AnnouncesView, self).get_context_data(**kwargs)
        context[ANNOUNCES] = Announce.get_and_check()
        return context


class NewsListView(TemplateView):
    template_name = NEWS + '/list.htm'

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        paginator = Paginator(News.objects.all(), NEWS_PER_PAGE)
        try:
            page = paginator.page(self.args[0])
            context[NEWS + '_list'] = _rowed_list(page.object_list, 3)
            context['pages'] = {
                'prev': (lambda: page.previous_page_number()
                         if page.has_previous() else False)(),
                'next': (lambda: page.next_page_number()
                         if page.has_next() else False)()
            }
        except EmptyPage:
            raise Http404
        return context


class NewsDetailView(TemplateView):
    template_name = NEWS + '/current.htm'

    def _get_page_by_obj(self, obj):
        paginator = Paginator(News.objects.all(), NEWS_PER_PAGE)
        for page in paginator.page_range:
            if obj in paginator.page(page).object_list: return page


    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)

        try:
            context['record'] = News.objects.get(id=self.args[0])
            context['page'] = self._get_page_by_obj(context['record'])
        except News.DoesNotExist:
            raise Http404

        try:
            context['images'] = context['record'].get_images()
        except AttributeError:
            context['images'] = False
        return context


class NewsPartnersView(JsonView):
    func = staticmethod(partners.get_partner_news)


class TourView(TemplateView):
    template_name = 'tour.htm'
    
    def get_context_data(self, **kwargs):
        context = super(TourView, self).get_context_data(**kwargs)
        context['calendar'] = tour.get_two_month(date.today())
        context['time'] = tour.WORK_HOURS
        context['captcha'] = get_yandex_captcha()
        return context
    
    def post(self, request, *args, **kwargs):
        response = tour.checker(request.POST)
        return HttpResponse(response,
                            content_type='application/json'
        )


class CaptchaView(JsonView):
    func = staticmethod(get_yandex_captcha)


class RezidentsView(TemplateView):
    template_name = 'rezidents.htm'

    def get_context_data(self, **kwargs):
        context = super(RezidentsView, self).get_context_data(**kwargs)
        context[REZIDENTS] = Rezidents.objects.all()
        return context
