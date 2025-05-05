from django.urls import path
from .views import *

urlpatterns = [
    path('bridge/', bridge, name='bridge'),
    #Volume
    path('volume_page/<int:journal_id>/', volume_page, name='volume_page'),
    path('add_volume/', add_volume, name='add_volume'),
    path('edit_volume/', edit_volume, name='edit_volume'),
    #Issue
    path('issues/<int:journal_id>/', issue_list, name='issue_list'),
    path('issues/save/', save_issue, name='save_issue'),
    #Article
    path('article_publish_page/<int:journal_id>/', article_publish_page, name='articles_page'),
    path('published_article/', publish_article, name='publish_article'),  # New URL for publishing
    #Get issue based on the volume for publishing
    path('get_issues_by_volume/', get_issues_by_volume, name='get_issues_by_volume'),
    #direct article publish
    path('publish_new_article/', publish_new_article, name='publish_new_article'),
    #Manuscript in processing
    path('manuscript-processing/<int:journal_id>/', manuscript_processing, name='manuscript_processing'),
    #Published article
    path('journal/<int:journal_id>/published_article/', published_article, name='published_article'),
    path('remove_article/<int:article_id>/', remove_article, name='remove_article'),

]
