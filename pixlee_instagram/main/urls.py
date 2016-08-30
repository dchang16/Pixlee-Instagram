from django.conf.urls import url
from . import views

app_name = 'main'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search$', views.search, name='search'),
    url(r'^enter_name', views.enter_name, name='enter_name'),
    url(r'^logout', views.delete_session, name='logout'),
    url(r'^search_tags', views.search_tags, name='search_tags'),
    url(r'^next_tag', views.next_tag, name='next_tag'),
    url(r'^prev_tag', views.prev_tag, name='prev_tag'),
    url(r'^show_collection', views.show_collection, name='show_collection'),
    url(r'^save_to_collection', views.save_to_collection, name='save_to_collection')

]
