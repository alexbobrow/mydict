from django.contrib.auth.views import LogoutView
from django.urls import path, include

from .views import WordsListView, StataView, AppTemplateView
from .views_api import NextView, ReportWordView, DeleteWordView, UpdateWordView, PreferenceUpdateView

api_urlpatterns = [
    path('next', NextView.as_view(), name='next'),
    path('report-word', ReportWordView.as_view(), name='report'),
    path('delete-word', DeleteWordView.as_view(), name='delete'),
    path('admin-update-word', UpdateWordView.as_view(), name='admin_update'),
    path('user-prefs', PreferenceUpdateView.as_view(), name='user_prefs'),
]

urlpatterns = [
    path('', AppTemplateView.as_view(template_name='about.html')),
    path('cards/', AppTemplateView.as_view(template_name='cards.html'), name='cards'),
    path('list/', WordsListView.as_view(), name='list'),
    path('logout', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/stata/', StataView.as_view(), name='stata'),

    path('api/', include(api_urlpatterns)),
]
