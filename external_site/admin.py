# -*- coding:utf-8 -*-
from django.contrib import admin
from external_site.models import News, Announce, Rezidents, Infrastructure, GalleryImage, GovermentOrg

class CommonJS(admin.ModelAdmin):

	class Media:
		js = (
			'/static/js/tinymce/tinymce.min.js',
			'/static/js/tinymce/tiny_mce_init.js',
			'/static/js/tinymce/tine_mce_float_left.js',
		)	


class CommonSixImages(admin.ModelAdmin):
	fieldsets = (
		(),
		("Дополнительные изображения", {
			'classes': ("collapse",),
			'fields': ('image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6')
		}),
	)

class NewsAdmin(CommonJS, CommonSixImages):
	list_display = ("id", "title", "date")
	fieldsets = (
		(None, {
			"fields": ("title", "sketch", "description", "image")
		}),
		(CommonSixImages.fieldsets[1]),
	)
	date_hierarchy = "date"


class RezidentsAdmin(CommonJS, CommonSixImages):
	list_display = ("id", "title")
	fieldsets = (
		(None, {
			"fields": ("title", "skills", "sketch", "description", "site", "mail", "tele", "image")
		}),
		(CommonSixImages.fieldsets[1]),
	)

class InfrastructureAdmin(CommonJS, CommonSixImages):
	list_display = ("id", "title")
	fieldsets = (
		(None, {
			"fields": ("title", "device", "sketch", "description", "image")
		}),
		(CommonSixImages.fieldsets[1]),
	)

class AnnounceAdmin(CommonJS):
	list_display = ("id", "title", "start_date")
	date_hierarchy = "start_date"

class GalleryImageAdmin(CommonJS):
	list_display = ("id", "comment")

class GovermentOrgAdmin(CommonJS):
	list_display = ("org",)

admin.site.register(News, NewsAdmin)
admin.site.register(Announce, AnnounceAdmin)
admin.site.register(Rezidents, RezidentsAdmin)
admin.site.register(Infrastructure, InfrastructureAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)
admin.site.register(GovermentOrg, GovermentOrgAdmin)
