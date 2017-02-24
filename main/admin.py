from django.contrib import admin

from .models import Word, Progress, Report


admin.site.register(Word)
admin.site.register(Progress)
admin.site.register(Report)