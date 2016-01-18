__author__ = 'jonesy'

from django.conf.urls import patterns, url, include
from dicer import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/$', views.about, name='about'),
        url(r'^add_category/$', views.add_category, name='add_category'), # NEW MAPPING!
        url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
        url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
        url(r'^category/(?P<category_name_slug>[\w\-]+)/add_post/$', views.add_post, name='add_post'),
        #url(r'^post_list/$', views.post_list, name='post_list'),
        #url(r'^category/(?P<category_name_slug>[\w\-]+)/post/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
        #url(r'^post/(?P<category_name_slug>[\w\-]+)/new/$', views.post_new, name='post_new'),
        #url(r'^category/(?P<category_name_slug>[\w\-]+)/post_new/$', views.post_new, name='post_new'),
        #url(r'^category/(?P<category_name_slug>[\w\-]+)/post/(?P<pk>[0-9]+)/edit/$', views.post_edit, name='post_edit'),
        #url(r'^register/$', views.register, name='register'),
        #url(r'^login/$', views.user_login, name='login'),
        #url(r'^search/$', views.search, name='search'),
        url(r'^goto/$', views.track_url, name='goto'),
        url(r'^like_category/$', views.like_category, name='like_category'),
        url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),
        url(r'^auto_add_page/$', views.auto_add_page, name='auto_add_page'),
        url(r'^restricted/', views.restricted, name='restricted'),)
        #url(r'^logout/$', views.user_logout, name='logout'),) # ADD NEW PATTERN!)

