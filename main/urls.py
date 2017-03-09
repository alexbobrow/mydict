from django.conf.urls import url
from . import views
from . import views_tmp as tmp


urlpatterns = [
    url(r'^$', views.root),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),


    url(r'^freq/cards/$', views.freq_cards, name='freq_cards'),
    url(r'^freq/list/$', views.freq_list, name='freq_list'),
    url(r'^own/cards/$', views.own_cards, name='own_cards'),
    url(r'^own/list/$', views.own_list, name='own_list'),


    url(r'^api/freq/next$', views.freq_next, name='freq_next'),
    url(r'^api/own/next$', views.own_next, name='own_next'),

    #url(r'^api/suggest$', views.suggest, name='suggest'),
    #url(r'^api/answer$', views.answer, name='answer'),
    url(r'^api/report-word$', views.report_word, name='report'),
    url(r'^api/skip-word$', views.skip_word, name='skip'),
    url(r'^api/delete-word$', views.delete_word, name='delete'),
    url(r'^api/update-word$', views.update_word, name='update'),

    url(r'^api/add-word$', views.add_word, name='add_word'),
    url(r'^api/remove-word$', views.remove_word, name='remove_word'),

    #url(r'^admin/stata/$', views.stata),    


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
