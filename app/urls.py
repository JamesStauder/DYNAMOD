from django.urls import path
from . import views
from django.conf.urls import url

#TODO: Add to all of these
urlpatterns = [

    url(r'^$', views.display_home, name='display_home'),
    url(r'^about/$', views.display_about, name='display_about'),
    url(r'^lessons/$', views.display_lessons, name='display_lessons'),
    url(r'^references/$', views.display_references, name='display_references'),
    url(r'^antarctica/$', views.display_antarctica, name='display_anarctica'),
    url(r'^greenland/$', views.display_greenland, name='display_greenland'),

    url(r'^ajax/get_flowline_with_data/$', views.get_flowline_with_data, name= 'get_flowline_with_data'),
    url(r'^ajax/get_point_data/$', views.get_point_data, name='get_point_data'),
    url(r'^ajax/run_model/$', views.run_model, name = 'run_model'),
]
