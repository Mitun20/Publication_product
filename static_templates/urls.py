# urls.py
from django.urls import path
from .views import *


urlpatterns = [
   
    path('about/', about, name='about'),
    path('about_ijam/', about_ijam, name='about_ijam'),
    path('about_jcm/', about_jcm, name='about_jcm'),
    path('about_jcs/', about_jcs, name='about_jcs'),
    path('aim_scope_ijam/', aim_scope_ijam, name='aim_scope_ijam'),
    path('aim_scope_jcm/', aim_scope_jcm, name='aim_scope_jcm'),
    path('aim_scope_jcs/', aim_scope_jcs, name='aim_scope_jcs'),
    path('author_center/', author_center, name='author_center'),
    path('authors_guidelines_ijam/', authors_guidelines_ijam, name='authors_guidelines_ijam'),
    path('authors_guidelines_jcm/', authors_guidelines_jcm, name='authors_guidelines_jcm'),
    path('authors_guidelines_jcs/', authors_guidelines_jcs, name='authors_guidelines_jcs'),
    path('contact/', contact, name='contact'),
    path('editorial_board_members_ijam/', editorial_board_members_ijam, name='editorial_board_members_ijam'),
    path('editorial_board_members_jcm/', editorial_board_members_jcm, name='editorial_board_members_jcm'),
    path('editorial_board_members_jcs/', editorial_board_members_jcs, name='editorial_board_members_jcs'),
    path('faq_karpagam_ijam/', faq_karpagam_ijam, name='faq_karpagam_ijam'),
    path('faq_karpagam_jcm/', faq_karpagam_jcm, name='faq_karpagam_jcm'),
    path('faq_karpagam_jcs/', faq_karpagam_jcs, name='faq_karpagam_jcs'),
    path('institutions/', institutions, name='institutions'),
    path('online_paper_submission/', online_paper_submission, name='online_paper_submission'),
    path('plagiarism_policy_ijam/', plagiarism_policy_ijam, name='plagiarism_policy_ijam'),
    path('plagiarism_policy_jcm/', about_ijam, name='plagiarism_policy_jcm'),
    path('plagiarism_policy_jcs/', plagiarism_policy_jcs, name='plagiarism_policy_jcs'),
    path('publication_fees/', publication_fees, name='publication_fees'),
    path('review_board_ijam/', review_board_ijam, name='review_board_ijam'),
    path('review_board_jcm/', review_board_jcm, name='review_board_jcm'),
    path('review_board_jcs/', review_board_jcs, name='review_board_jcs'),
    path('reviewer_policy_ijam/', reviewer_policy_ijam, name='reviewer_policy_ijam'),
    path('reviewer_policy_jcm/', reviewer_policy_jcm, name='reviewer_policy_jcm'),
    path('reviewer_policy_jcs/', reviewer_policy_jcs, name='reviewer_policy_jcs'),
    path('subscription_ijam/', subscription_ijam, name='subscription_ijam'),
    path('subscription_jcm/', subscription_jcm, name='subscription_jcm'),
    path('subscription_jcs/', subscription_jcs, name='subscription_jcs'),
    path('terms_and_conditions/', terms_and_conditions, name='terms_and_conditions'),

     
    ]