from django.contrib import admin

from .models import Word, Progress, Report, Preferences


admin.site.register(Word)
admin.site.register(Progress)
admin.site.register(Report)
admin.site.register(Preferences)