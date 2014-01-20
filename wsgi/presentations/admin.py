from django.contrib import admin

from .models import Presentation


class PresentationAdmin(admin.ModelAdmin):
    list_display = ('summary', 'speaker')
admin.site.register(Presentation, PresentationAdmin)
