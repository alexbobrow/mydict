from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView

from . import views
from .views import WordsListView, StataView

urlpatterns = [
    path('', TemplateView.as_view(template_name='about.html')),
    path('cards/', TemplateView.as_view(template_name='cards.html'), name='cards'),
    path('list/', WordsListView.as_view(), name='list'),
    path('logout', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/stata/', StataView.as_view(), name='stata'),

    path('api/next', views.next, name='next'),
    path('api/report-word', views.report_word, name='report'),
    path('api/delete-word', views.delete_word, name='delete'),
    path('api/admin-update-word', views.admin_update_word, name='admin_update'),
    path('api/user-prefs/', views.user_prefs, name='user_prefs'),
]
