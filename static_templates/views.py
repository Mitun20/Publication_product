from django.shortcuts import render

from oss.models import Journal
from django.shortcuts import render
from dl.models import Volume, Issue


# Create your views here.

def about(request):
    journals = Journal.objects.all()

    return render(request, 'about.html',{'journals': journals})

def about_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'about_ijam.html',{'journals': journals})

def about_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'about_jcm.html',{'journals': journals})

def about_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'about_jcs.html',{'journals': journals})

def aim_scope_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'aim_scope_ijam.html',{'journals': journals})

def aim_scope_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'aim_scope_jcm.html',{'journals': journals})

def aim_scope_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'aim_scope_jcs.html',{'journals': journals})

def author_center(request):
    journals = Journal.objects.all()
    
    return render(request, 'author_center.html',{'journals': journals})

def authors_guidelines_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'authors_guidelines_ijam.html',{'journals': journals})

def authors_guidelines_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'authors_guidelines_jcm.html',{'journals': journals})

def authors_guidelines_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'authors_guidelines_jcs.html',{'journals': journals})

def contact(request):
    journals = Journal.objects.all()
    
    return render(request, 'contact.html',{'journals': journals})


def editorial_board_members_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'editorial_board_members_ijam.html',{'journals': journals})

def editorial_board_members_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'editorial_board_members_jcm.html',{'journals': journals})

def editorial_board_members_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'editorial_board_members_jcs.html',{'journals': journals})

def faq_karpagam_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'faq_karpagam_ijam.html',{'journals': journals})

def faq_karpagam_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'faq_karpagam_jcm.html',{'journals': journals})

def faq_karpagam_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'faq_karpagam_jcs.html',{'journals': journals})

def institutions(request):
    
    return render(request, 'institutions.html')

def online_paper_submission(request):
    journals = Journal.objects.all()
    
    return render(request, 'online_paper_submission.html',{'journals': journals})

def plagiarism_policy_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'plagiarism_policy_ijam.html',{'journals': journals})

def plagiarism_policy_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'plagiarism_policy_jcm.html',{'journals': journals})

def plagiarism_policy_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'plagiarism_policy_jcs.html',{'journals': journals})

def publication_fees(request):
    journals = Journal.objects.all()
    
    return render(request, 'publication_fees.html',{'journals': journals})

def review_board_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'review_board_ijam.html',{'journals': journals})

def review_board_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'review_board_jcm.html',{'journals': journals})

def review_board_jcs(request):
    journals = Journal.objects.all()

    return render(request, 'review_board_jcs.html',{'journals': journals})

def reviewer_policy_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'reviewer_policy_ijam.html',{'journals': journals})

def reviewer_policy_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'reviewer_policy_jcm.html',{'journals': journals})

def reviewer_policy_jcs(request):
    journals = Journal.objects.all()
    
    return render(request, 'reviewer_policy_jcs.html',{'journals': journals})

def subscription_ijam(request):
    journals = Journal.objects.all()
    return render(request, 'subscription_ijam.html',{'journals': journals})

def subscription_jcm(request):
    journals = Journal.objects.all()
    return render(request, 'subscription_jcm.html',{'journals': journals})

def subscription_jcs(request):
    journals = Journal.objects.all()
    
   
    return render(request, 'subscription_jcs.html',{'journals': journals})

def terms_and_conditions(request):
    journals = Journal.objects.all()
    
    return render(request, 'terms_and_conditions.html',{'journals': journals})
