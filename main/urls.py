from django.urls import path

from . import views

urlpatterns = [
    path('', views.root),
    path('logout', views.logout_view, name='logout'),
    path('cards/', views.cards, name='cards'),
    path('list/', views.list, name='list'),
    path('api/next', views.next, name='next'),
    path('api/report-word', views.report_word, name='report'),
    path('api/delete-word', views.delete_word, name='delete'),
    path('api/admin-update-word', views.admin_update_word, name='admin_update'),
    path('api/user-prefs/', views.user_prefs, name='user_prefs'),
    path('admin/stata/', views.stata, name='stata'),
]
