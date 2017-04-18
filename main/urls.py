from django.conf.urls import url
from . import views
from . import views_tmp as tmp


urlpatterns = [
    url(r'^$', views.root),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),


    url(r'^cards/$', views.cards, name='cards'),
    url(r'^list/$', views.list, name='list'),

    url(r'^api/next$', views.next, name='next'),

    url(r'^api/report-word$', views.report_word, name='report'),
    url(r'^api/delete-word$', views.delete_word, name='delete'),
    url(r'^api/admin-update-word$', views.admin_update_word, name='admin_update'),
    url(r'^api/user-prefs/$', views.user_prefs, name='user_prefs'),


    url(r'^admin/stata/$', views.stata, name='stata'),


    #url(r'^tmp/list$', tmp.list),
    #url(r'^tmp/control$', tmp.control),
    #url(r'^tmp/add-import$', tmp.add_import),   
    #url(r'^api/tmp/create-from-txt$', tmp.create_from_txt),  
    #url(r'^api/tmp/combine$', tmp.combine),
    #url(r'^api/tmp/rename$', tmp.rename),
    #url(r'^api/tmp/delete$', tmp.delete),
    #url(r'^api/tmp/autocomplete$', tmp.autocomplete),
    #url(r'^api/tmp/next$', tmp.next_for_translate),
    #url(r'^api/tmp/trs$', tmp.save_translation),
    #url(r'^api/tmp/import$', tmp.import2),


    


]
