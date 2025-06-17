from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from account.models import FeedbackType, Question
from oss.models import Article_Status, Journal, Accepted_Submission, Submission
from .models import *
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required , user_passes_test

from oss.auth import is_super_admin
# Create your views here.

#from accounts to DL
def bridge(request):
    if request.method == 'POST':
        journal_id = request.POST.get('journal_id')
        if not journal_id:
            return JsonResponse({'status': 'error', 'message': 'No journal ID provided'})

        try:
            journal = Journal.objects.get(id=journal_id)
            # Process the journal data as needed

            # Assuming you have a URL pattern named 'journal_detail' to display journal details
            redirect_url = reverse('volume_page', args=[journal_id])
            return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
        except Journal.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Journal not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@user_passes_test(is_super_admin)
def volume_page(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    volumes = Volume.objects.filter(journal=journal).order_by('-id')
    latest_issue = Issue.objects.filter(volume__journal=journal).order_by('-id').first()
    latest_year = volumes.first().year if volumes.exists() else None

    context = {
        'journal': journal,
        'volumes': volumes,
        'latest_issue': latest_issue,
        'latest_year': latest_year,
    }
    return render(request, 'volume_page.html', context)


# def volume_page(request, journal_id):
#     journal = get_object_or_404(Journal, id=journal_id)
#     volumes = Volume.objects.filter(journal=journal).order_by('-id')
#     context = {
#         'journal': journal,
#         'volumes': volumes,
#     }
#     return render(request, 'volume_page.html', context)

def add_volume(request):
    if request.method == 'POST':
        volume = request.POST.get('volume')
        description = request.POST.get('description')
        year = request.POST.get('year')
        journal_id = request.POST.get('journal_id')
        journal = get_object_or_404(Journal, id=journal_id)

        Volume.objects.create(volume=volume, description=description, year=year, journal=journal)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def edit_volume(request):
    if request.method == 'POST':
        volume_id = request.POST.get('id')
        volume = request.POST.get('volume')
        description = request.POST.get('description')
        year = request.POST.get('year')

        volume_instance = get_object_or_404(Volume, id=volume_id)
        volume_instance.volume = volume
        volume_instance.description = description
        volume_instance.year = year
        volume_instance.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


#***********************************************
@login_required
@user_passes_test(is_super_admin)
def issue_list(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    volumes = Volume.objects.filter(journal_id=journal_id).order_by('-id')
    issues = Issue.objects.filter(volume__in=volumes).order_by('-id')
    return render(request, 'issue_list.html', { 'issues': issues,'volumes': volumes,'journal': journal})



def save_issue(request):
    if request.method == 'POST':
        issue_id = request.POST.get('issueId')
        issue_text = request.POST.get('issue')
        volume_id = request.POST.get('volume')
        description = request.POST.get('description')

        if not issue_text or not volume_id or not description:
            return JsonResponse({'success': False, 'error': 'All fields are required'})

        try:
            volume = Volume.objects.get(id=volume_id)
        except Volume.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Volume not found'})

        if issue_id:  # Update existing issue
            issue = get_object_or_404(Issue, id=issue_id)
            issue.issue = issue_text
            issue.volume = volume
            issue.description = description
        else:  # Create new issue
            issue = Issue(issue=issue_text, volume=volume, description=description)

        issue.save()

        return JsonResponse({
            'success': True,
            'issue': {
                'id': issue.id,
                'issue': issue.issue,
                'volume_id': issue.volume.id,
                'volume': issue.volume.volume,
                'description': issue.description,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



#***********************************************************
@login_required
@user_passes_test(is_super_admin)
def article_publish_page(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    accepted_submissions = Accepted_Submission.objects.filter(
        submission__journal=journal,
        submission__article_status__article_status='Proof Read Done'
    )
    issues = Issue.objects.filter(volume__journal__id=journal_id).order_by('-id')  # Latest first
    volumes = Volume.objects.filter(journal_id=journal_id).order_by('-id')  # Latest first
    
    # Get the most recent volume and issue
    latest_volume = volumes.first()
    latest_issue = issues.filter(volume=latest_volume).first() if latest_volume else None

    context = {
        'journal': journal,
        'accepted_submissions': accepted_submissions,
        # 'issues': issues,
        'volumes': volumes,
        'latest_volume_id': latest_volume.id if latest_volume else None,
        # 'latest_issue_id': latest_issue.id if latest_issue else None,
    }
    return render(request, 'article_publish_page.html', context)

def publish_article(request):
    if request.method == 'POST':
        try:
            acceptedSubmission_id = request.POST.get('accepted_submission_id')
            issue = request.POST.get('issue_id')
            published_on = request.POST.get('published_on')

            accepted_submission = Accepted_Submission.objects.get(id=acceptedSubmission_id)
            # title=Accepted_Submission.objects.get(corrected_title=accepted_submission.corrected_title)
            # typeset_file=Accepted_Submission.objects.get(typeset_file= accepted_submission.typeset_file)

            published_article, created = Published_article.objects.get_or_create(
                accepted_submission=accepted_submission,
                issue_id=issue,
                published_on_date=published_on,
                title = accepted_submission.corrected_title,
                file=accepted_submission.typeset_file,
                doi='your-doi-here',
                area=accepted_submission.submission.specialization if accepted_submission.submission.specialization else None,
            )

            published_status = Article_Status.objects.get(article_status='Published')
            accepted_submission.submission.article_status = published_status
            accepted_submission.submission.save()

            # Confirm success
            return JsonResponse({'success': True, 'message': 'Article published successfully!'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})



#************************************direct publish*******************

def publish_new_article(request):
    if request.method == 'POST':
        try:
            volume_id = request.POST.get('volume_id')
            issue_id = request.POST.get('issue_id')
            published_on = request.POST.get('published_on')
            title = request.POST.get('title')
            abstract = request.POST.get('abstract')
            author = request.POST.get('author')
            file = request.FILES.get('file')

            volume = Volume.objects.get(id=volume_id)
            issue = Issue.objects.get(id=issue_id)

            published_article = Published_article.objects.create(
                issue=issue,
                published_on_date=published_on,
                doi='your-doi-here'
            )
            
            published_article.title = title
            published_article.abstract = abstract
            published_article.author = author
            published_article.file = file
            published_article.save()

            return JsonResponse({'success': True, 'message': 'New article published successfully!'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


def get_issues_by_volume(request):
    volume_id = request.GET.get('volume_id')
    
    if not volume_id:
        logger.error("No volume_id provided in the request")
        return JsonResponse({'error': 'No volume_id provided'}, status=400)

    try:
        issues = Issue.objects.filter(volume_id=volume_id).order_by('-id')  # Latest first
        issues_list = [{'id': issue.id, 'issue': issue.issue} for issue in issues]
        
        logger.info(f"Retrieved {len(issues_list)} issues for volume_id {volume_id}")
        logger.debug(f"Issues list: {issues_list}")
        
        return JsonResponse({'issues': issues_list})
    except ObjectDoesNotExist:
        logger.error(f"Volume with id {volume_id} does not exist")
        return JsonResponse({'error': 'Volume not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error retrieving issues for volume_id {volume_id}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
    
# ************************************Manuscript in Processing***************************************************
from .forms import SubmissionStatusForm
from django.core.paginator import Paginator
@login_required
@user_passes_test(is_super_admin)

def manuscript_processing(request, journal_id):
    # Get the Published status object
    published_status = Article_Status.objects.get(article_status='Published')
    
    # Get the journal object
    journal = Journal.objects.get(id=journal_id)
    
    # Get all submissions for the specified journal excluding the Published status
    submissions = Submission.objects.filter(journal=journal).exclude(article_status=published_status)

    # Filter based on article status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        submissions = submissions.filter(article_status__article_status=status_filter)

    # Handle status update
    if request.method == 'POST':
        form = SubmissionStatusForm(request.POST)
        if form.is_valid():
            submission_id = form.cleaned_data['submission_id']
            new_status_id = form.cleaned_data['article_status']
            Submission.objects.filter(id=submission_id).update(article_status_id=new_status_id)
            return redirect('manuscript_processing', journal_id=journal_id)

    # Initialize the form for changing status
    form = SubmissionStatusForm()

    # Get all possible article statuses for the filter dropdown, excluding Published
    article_status_filter = Article_Status.objects.exclude(id=published_status.id)

    # Get specific article statuses for the Status change dropdown
    desired_statuses = ['Awaiting for EIC Decision', 'Awaiting AE Recommendation', 'Under Review', 'AE Assigned', 'Submitted']
    article_status_change = Article_Status.objects.filter(article_status__in=desired_statuses).exclude(id=published_status.id)

    # Pagination
    paginator = Paginator(submissions, 2)  # Show 20 submissions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manuscripts_in_process.html', {
        'journal': journal,
        'submissions': page_obj,
        'form': form,
        'article_status_filter': article_status_filter,
        'article_status_change': article_status_change,
        'page_obj': page_obj,
    })


# **************************Published article*************************************************************

from django.db.models import Q


@login_required
@user_passes_test(is_super_admin)
def published_article(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    volumes = Volume.objects.filter(journal=journal)
    issues = Issue.objects.filter(volume__journal=journal)
    
    selected_volume = request.GET.get('volume')
    selected_issue = request.GET.get('issue')

    filter_criteria = Q(issue__volume__journal=journal)
    if selected_volume  and selected_volume != 'None':
        filter_criteria &= Q(issue__volume_id=selected_volume)
    if selected_issue and selected_issue != 'None':
        filter_criteria &= Q(issue_id=selected_issue)

    articles = Published_article.objects.filter(filter_criteria).select_related('issue__volume').all()
    

    for article in articles:
        if article.accepted_submission is None:
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': article.title,
                'authors': article.author,
            }
        else:
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': article.accepted_submission.corrected_title,
                'authors': article.accepted_submission.submission.author.user.get_full_name(),
            }
        article.article_data = article_data

    paginator = Paginator(articles, 20)  # Show 20 articles per page
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'articles': articles,
        'volumes': volumes,
        'issues': issues,
        'selected_volume': selected_volume,
        'selected_issue': selected_issue,
        'journal': journal,
        'feedback_types': FeedbackType.objects.all(),
        'all_questions': Question.objects.all(),
    }
    return render(request, 'published_article.html', context)


def remove_article(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(Published_article, id=article_id)
        if article.accepted_submission is None:
            article.delete()
        else:
            proof_read_status = get_object_or_404(Article_Status, article_status="Proof Read Done")
            submission = article.accepted_submission.submission
            submission.article_status = proof_read_status
            submission.save()
            article.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Article marked as Proof Read.'})
        
        # Redirect to the published articles page with the journal_id
        journal_id = article.issue.volume.journal.id
        return redirect('published_article', journal_id=journal_id)
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})