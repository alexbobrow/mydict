from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.root),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^cards/$', views.cards, name='cards'),
    url(r'^list/$', views.list, name='list'),
    url(r'^api/next$', views.next, name='next'),
    url(r'^api/report-word$', views.report_word, name='report'),
    url(r'^api/delete-word$', views.delete_word, name='delete'),
    url(r'^api/admin-update-word$', views.admin_update_word, name='admin_update'),
    url(r'^api/user-prefs/$', views.user_prefs, name='user_prefs'),
    url(r'^admin/stata/$', views.stata, name='stata'),
]
