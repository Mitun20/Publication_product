from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login ,logout
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth import authenticate, login
from django.db import IntegrityError  
from oss.services import send_email
from .forms import *
from oss.forms import *
from oss.auth import *
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import logging
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .forms import UserRegistrationForm
from .models import Author, User,Editor
from django.contrib.auth.forms import SetPasswordForm
from oss.models import CoAuthor, Journal, Journal_Editor_Assignment
from django.contrib.auth.forms import SetPasswordForm     #set_new_password
from django.contrib.auth import views as auth_views       #CustomPasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm   #CustomPasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm   #password_reset_view
from django.contrib.auth.views import PasswordChangeView  #CustomPasswordChangeView
from django.urls import reverse_lazy                      #CustomPasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin 
import json
from django.core.paginator import Paginator
from dl.models import Published_article, Issue
from dl .models import *



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#**************logout****************

def custom_logout(request):
    logout(request)
    return redirect('login')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('user_management')  # Redirect to user_management.html
                elif user.groups.filter(name='Admin Office').exists():
                    return redirect('admin_office')  # Redirect to admin_office.html
                elif user.groups.filter(name='AE').exists():
                    return redirect('associate_editor')  # Redirect to AE dashboard or specific view
                elif user.groups.filter(name='EIC').exists():
                    return redirect('editor_in_chief')  # Redirect to EIC dashboard or specific view
                elif user.groups.filter(name='Author').exists():
                    return redirect('startnew')  # Redirect to Author dashboard or specific view
                elif user.groups.filter(name='Reviewer').exists():
                    return redirect('reviewer_invitations')  # Redirect to Reviewer dashboard or specific view
                else:
                    return redirect('change_password')  # Redirect to a general view for other users
            else:
                form.add_error(None, 'Invalid username or password')
        else:
            form.add_error(None, 'Form is not valid')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
 
 
# -------------------------------------------------------------------------------------user_management--------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_super_admin)
def user_management(request):
    users_list = User.objects.all().order_by('-id')

    paginator = Paginator(users_list,20)  # Show 20 users per page.
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    journal_usernames = list(User.objects.filter(groups__name__in=['AE', 'EIC']).values_list('username', flat=True))
    dates = Date.objects.all()
    context = {
        'users': users,
        'journal_usernames': json.dumps(journal_usernames), 
        'journals' : Journal.objects.all() ,# Convert list to JSON string
        'dates': dates,
    }
    return render(request, 'user_management.html', context)


# --------------------Create user------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
@user_passes_test(is_super_admin)
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active') == 'true'

        if not email:
            return JsonResponse({'success': False, 'error': 'Email is required'})

        username = email  # Set the username as the email

        try:
            temp_password = get_random_string(length=8)  # Generate a random temporary password
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=temp_password,  # Use the generated random password
                is_active=is_active
            )
            
            send_email(
                    to_email=user.email,
                    subject='Your account has been created',
                    template_name='email_templates/account_created.html',
                    user=user,
                    context={'user': user }
                )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# --------------------Assign Roles------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# @require_GET
# def fetch_groups(request):
#     username = request.GET.get('username')
#     user = User.objects.get(username=username)
#     groups = Group.objects.all()
#     user_groups = user.groups.values_list('id', flat=True)
#     groups_data = [{'id': group.id, 'name': group.name} for group in groups]
#     return JsonResponse({'groups': groups_data, 'user_groups': list(user_groups)})



# @require_POST
# def update_user_groups(request):
#     username = request.POST.get('username')
#     groups = request.POST.getlist('groups[]')
#     user = get_object_or_404(User, username=username)
#     user.groups.clear()
#     ae_group = Group.objects.get(name='AE')
#     eic_group = Group.objects.get(name='EIC')
#     admin_group = Group.objects.get(name='Admin Office')
#     verification_link = f"{settings.SITE_URL}{reverse('login')}"
#     for group_id in groups:
#         group = get_object_or_404(Group, id=group_id)
#         user.groups.add(group)

#     # Collect all assigned groups
#     assigned_groups = []

#     # Assign new groups and collect the group names
#     for group_id in groups:
#         group = get_object_or_404(Group, id=group_id)
#         user.groups.add(group)
#         assigned_groups.append(group.name)

#     # Send a single email with all roles assigned
#     if assigned_groups:
#         send_email(
#             to_email=user.email,
#             subject='Roles assigned to you',
#             template_name='email_templates/admin_role.html',
#             user=user,
#             context={'user': user, 'assigned_groups': assigned_groups,'verification_link':verification_link}
#         )
#     # Check if user has AE or EIC roles and update Editor model
#     if ae_group in user.groups.all() or eic_group in user.groups.all():
#         editor, created = Editor.objects.get_or_create(user=user)
#         editor.is_active = True
#         editor.save()
#     else:
#         # If user doesn't have AE or EIC roles, remove from Editor model
#         Editor.objects.filter(user=user).delete()

#     return JsonResponse({'status': 'success'})
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from oss.models import Specialization, Reviewer_Specialization
# from your_app.email_utils import send_email  # Adjust import based on your setup
from django.conf import settings
from django.urls import reverse

@require_GET
def fetch_groups(request):
    username = request.GET.get('username')
    user = User.objects.get(username=username)
    groups = Group.objects.all()
    user_groups = user.groups.values_list('id', flat=True)
    groups_data = [{'id': group.id, 'name': group.name} for group in groups]
    
    # Fetch specializations
    specializations = Specialization.objects.all()
    specializations_data = [{'id': spec.id, 'specialization': spec.specialization} for spec in specializations]
    print("Specializations:", specializations_data)
    # Get Reviewer group ID
    reviewer_group = Group.objects.get(name='Reviewer')
    
    return JsonResponse({
        'groups': groups_data,
        'user_groups': list(user_groups),
        'specializations': specializations_data,
        'reviewer_group_id': reviewer_group.id
    })

@require_GET
def fetch_reviewer_specializations(request):
    username = request.GET.get('username')
    user = User.objects.get(username=username)
    reviewer_specs = Reviewer_Specialization.objects.filter(reviewer=user).values_list('specialization__id', flat=True)
    return JsonResponse({'specialization_ids': list(reviewer_specs)})

@require_POST
def update_user_groups(request):
    username = request.POST.get('username')
    groups = request.POST.getlist('groups[]')  # Changed to groups[] to match jQuery serialization
    specializations = request.POST.getlist('specializations[]')  # Get specializations
    user = get_object_or_404(User, username=username)
    
    # Clear existing groups
    user.groups.clear()
    
    ae_group = Group.objects.get(name='AE')
    eic_group = Group.objects.get(name='EIC')
    admin_group = Group.objects.get(name='Admin Office')
    reviewer_group = Group.objects.get(name='Reviewer')
    verification_link = f"{settings.SITE_URL}{reverse('login')}"
    
    # Assign new groups
    assigned_groups = []
    for group_id in groups:
        group = get_object_or_404(Group, id=group_id)
        user.groups.add(group)
        if group.name == 'Reviewer':
            Author.objects.create(
            user=user,
            title=Title.objects.all().first(),  # Assuming you want to set the first title
            institution='update',
            address='update',
            city='update',
            state='update',
            country=Country.objects.get(country='India'),  # Assuming you want to set the first country
            mobile_no='update',
            is_reviewer=True,
            )
        assigned_groups.append(group.name)
    
    # Handle Reviewer specializations
    if str(reviewer_group.id) in groups:
        # Clear existing specializations for this user
        Reviewer_Specialization.objects.filter(reviewer=user).delete()
        # Add new specializations
        for spec_id in specializations:
            specialization = get_object_or_404(Specialization, id=spec_id)
            Reviewer_Specialization.objects.create(reviewer=user, specialization=specialization)
    
    # Send email with all assigned roles
    if assigned_groups:
        send_email(
            to_email=user.email,
            subject='Roles assigned to you',
            template_name='email_templates/admin_role.html',
            user=user,
            context={'user': user, 'assigned_groups': assigned_groups, 'verification_link': verification_link}
        )
    
    # Update Editor model for AE/EIC roles
    if ae_group in user.groups.all() or eic_group in user.groups.all():
        editor, created = Editor.objects.get_or_create(user=user)
        editor.is_active = True
        editor.save()
    else:
        Editor.objects.filter(user=user).delete()

    return JsonResponse({'status': 'success'})


@require_POST
def add_specialization(request):
    new_specialization = request.POST.get('newSpecialization')
    if not new_specialization:
        return JsonResponse({'success': False, 'error': 'Specialization name is required.'})

    # Create and save the new specialization
    specialization = Specialization(specialization=new_specialization)
    specialization.save()

    return JsonResponse({'success': True})

# @require_GET
# def fetch_specializations(request):
#     specializations = Specialization.objects.all()
#     specializations_data = [{'id': spec.id, 'specialization': spec.specialization} for spec in specializations]
#     return JsonResponse({'specializations': specializations_data})

# --------------------Reset User Password------------------------------------------------------------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
@login_required
@user_passes_test(is_super_admin)
def reset_user_password(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            new_password = request.POST['new_password']
            email = request.POST['email']
            
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            verification_link = f"{settings.SITE_URL}{reverse('change_password')}"

            context = {
                'username': username,
                'new_password': new_password,
                'verification_link': verification_link,
            }

            
            send_email(
                to_email=email,
                subject='Your password has been reset',
                template_name='email_templates/reset_password_email.html',
                user=user,
                context=context
            )
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")  # Log the error
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

# --------------------Journal Assign------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_journals(request):
    username = request.GET.get('username')
    editor = Editor.objects.filter(user__username=username).first()
    
    journals = Journal.objects.all()
    assigned_journal = Journal_Editor_Assignment.objects.filter(editor=editor).first()
    
    data = {
        'journals': list(journals.all().values('id', 'title')),
        'selected_journal': assigned_journal.journal.id if assigned_journal else None
    }
    
    return JsonResponse(data)
@login_required
@user_passes_test(is_super_admin)
def assign_journal(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        journal_id = request.POST.get('journal_id')
        if not username or not journal_id:
            return JsonResponse({'success': False, 'error': 'Username or Journal ID is missing.'})
        try:
            # Get the User object based on the username
            user = get_object_or_404(User, username=username)
            # Get the Journal object based on the journal_id
            journal = get_object_or_404(Journal, id=journal_id)
            # Get or create the Editor object associated with the User
            editor, created = Editor.objects.get_or_create(user=user)
            # Remove existing journal assignments for the editor
            Journal_Editor_Assignment.objects.filter(editor=editor).delete()
            # Assign the selected journal to the editor
            Journal_Editor_Assignment.objects.create(journal=journal, editor=editor)
            verification_link = f"{settings.SITE_URL}{reverse('login')}"
            context = {
                'username': username,
                'journal_name': journal.title,
                'verification_link':verification_link,
            }

            # Send email
            send_email(
                to_email=user.email,
                subject='Regarding Journal Assignment',
                template_name='email_templates/journal_assignment_email.html',
                user=user,
                context=context
            )
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist.'})
        except Journal.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Journal does not exist.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# -----------------------------------------------------------------------------------Publication Management---------------------------------------------------------------------------------------------------------


@login_required
@user_passes_test(is_super_admin)
def publication_management(request):
    context = {
        'journals' : Journal.objects.all() ,# Convert list to JSON string
    }
    return render(request, 'publication_management.html', context)

def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(first_name__icontains=query) | User.objects.filter(username__icontains=query)
    users_data = list(users.values('first_name', 'last_name', 'username', 'email', 'is_superuser'))

    journal_usernames = list(User.objects.filter(groups__name__in=['AE', 'EIC']).values_list('username', flat=True))
    return JsonResponse({'users': users_data, 'journal_usernames': journal_usernames})


# --------------------------------------------------------------------------------------Date Settings---------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_super_admin)
def date_settings(request):
    if request.method == 'POST':
        journal_id = request.POST.get('journal_id')
        journal = get_object_or_404(Journal, id=journal_id)
        date_instance, created = Date.objects.get_or_create(journal=journal)

        date_instance.due_days_to_accept_invitation = request.POST.get('due_days_to_accept_invitation')
        date_instance.due_days_to_review = request.POST.get('due_days_to_review')
        date_instance.due_days_to_minor_revision = request.POST.get('due_days_to_minor_revision')
        date_instance.due_days_to_major_revision = request.POST.get('due_days_to_major_revision')
        date_instance.due_days_to_payment = request.POST.get('due_days_to_payment')
        date_instance.due_days_to_corrections = request.POST.get('due_days_to_corrections')
        date_instance.due_days_to_typeset_approval = request.POST.get('due_days_to_typeset_approval')
        date_instance.due_days_to_next_step = request.POST.get('due_days_to_next_step')
        date_instance.save()

        return redirect('date_settings')  # Redirect to the same page after submission

    journals = Journal.objects.all()
    dates = {date.journal_id: date for date in Date.objects.all()}
    return render(request, 'date_settings.html', {'journals': journals, 'dates': dates})


# ------------------------------------------------------------------------Index home page ---------------------------------------------------------------------------------------
from django.db.models import Q


def index(request):

    journals = Journal.objects.all()
    # journal_name = "JCS"  # The name of the journal to filter by
    journal = Journal.objects.get(title="JCS")  # Assuming 'name' is a unique field in Journal model
    
    volumes = Volume.objects.filter(journal=journal)
    latest_issues = Issue.objects.filter(volume__journal=journal).order_by('-id')[:6]  # Fetch the latest 3 issues for the journal
    
    jcs_journal = Journal.objects.get(title='JCS')  # Adjust according to your Journal model

    # Get the latest volume for the JCS journal
    latest_volume = Volume.objects.filter(journal=jcs_journal).order_by('-year', '-volume').first()
    
    if latest_volume:
        # Get the latest issue for the latest volume
        latest_issue = Issue.objects.filter(volume=latest_volume).order_by('-issue').first()

        if latest_issue:
            # Get the latest published articles for the latest issue
            latest_articles = Published_article.objects.filter(issue=latest_issue).order_by('-id')
        else:
            latest_articles = []
    else:
        latest_articles = []
    user = request.user
    has_ae_or_eic = user.groups.filter(name__in=['AE', 'EIC']).exists()
    has_author_or_reviewer = user.groups.filter(name__in=['Author', 'Reviewer']).exists()
     # Handle search functionality
     
    for article in latest_articles:
        accepted_submission = article.accepted_submission
        if accepted_submission and accepted_submission.submission:
            submission = accepted_submission.submission
            co_authors = CoAuthor.objects.filter(submission=submission)
            article.co_authors = co_authors if co_authors.exists() else None
            article_data = {
                'volume': article.issue.volume.volume,
                'year': article.issue.volume.year,
                'issue': article.issue.issue,
                'title': accepted_submission.corrected_title,
                'authors': submission.author.user.get_full_name(),
                'file': accepted_submission.typeset_file
            }
        else:
            article_data = {
                'volume': article.issue.volume.volume,
                'year': article.issue.volume.year,
                'issue': article.issue.issue,
                'title': article.title,
                'authors': article.author,
                'file': article.file,
            }
        article.article_data = article_data
    search_query = request.GET.get('query', '')
    search_results = []
    if search_query:
        search_results = Published_article.objects.filter(
            Q(title__icontains=search_query)
        ).distinct()

    top_downloaded_articles = Published_article.objects.order_by('-download_count')[:3]
    context = {
        'journal': journal,
        'journals': journals,
        'volumes': volumes,
        'latest_issues': latest_issues,
        'latest_issue': latest_issue,
        'latest_articles': latest_articles,
        'has_ae_or_eic': has_ae_or_eic,
        'has_author_or_reviewer': has_author_or_reviewer,
        'search_results': search_results,
        'search_query': search_query,
        'top_downloaded_articles': top_downloaded_articles,
        'latest_volume':latest_volume,
    }
    return render(request, 'index.html', context)





def check_user_status(request):
    user = request.user
    return JsonResponse({
        'is_authenticated': user.is_authenticated,
        'is_author': user.groups.filter(name='Author').exists(),
    })


# -------register------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from django.db import IntegrityError  

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Process the valid form data
            user = form.save(commit=False)
            try:
                user.username = form.cleaned_data.get('email')
                user.is_active = False
                user.save()
                user.refresh_from_db()
            
                phone_code = request.POST.get('phone_code')
                mobile_no = form.cleaned_data.get('mobile_no')
                full_mobile_no = f"{phone_code}{mobile_no}"
            
                author = Author(
                    user=user,
                    title=form.cleaned_data.get('title'),
                    institution=form.cleaned_data.get('institution'),
                    address=form.cleaned_data.get('address'),
                    city=form.cleaned_data.get('city'),
                    state=form.cleaned_data.get('state'),
                    country=form.cleaned_data.get('country'),
                    mobile_no=full_mobile_no,
                    zipcode=form.cleaned_data.get('zipcode'),
                    orcid_id=form.cleaned_data.get('orcid_id'),
                    scopus_id=form.cleaned_data.get('scopus_id'),
                )
                author.save()
                token = generate_token(user)
                uid = encode_uid(user)
                verification_link = f"{settings.SITE_URL}{reverse('set_new_password', kwargs={'uidb64': uid, 'token': token})}"
        
                send_email(
                        to_email=user.email,
                        subject='Registration Success',
                        template_name='email_templates/registration_success.html',
                        user=user,
                        context={'user': user ,'verification_link': verification_link,}
                    )
                
                return redirect('registration_complete')
            except IntegrityError:
                form.add_error('email', 'This email address is already registered.')
       
            # If form is not valid, render the form with errors
            countries = Country.objects.all()
            return render(request, 'register.html', {'form': form, 'countries': countries})
    else:
        form = UserRegistrationForm()
        countries = Country.objects.all()
        return render(request, 'register.html', {'form': form, 'countries': countries})
# ----Mail Verification------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_token(user):
    return default_token_generator.make_token(user)

def encode_uid(user):
    return urlsafe_base64_encode(force_bytes(user.pk))

def decode_uid(uid):
    return force_str(urlsafe_base64_decode(uid))

def registration_complete(request):
    return render(request, 'registration_complete.html')

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        logger.error(f'User does not exist or token is invalid: uidb64={uidb64}, token={token}')
    
    if user is not None and default_token_generator.check_token(user, token):
        return redirect('set_new_password', uidb64=uidb64, token=token)
    else:
        logger.error(f'Token verification failed: uidb64={uidb64}, token={token}')
        return render(request, 'email_verification_failed.html')

    
# ------Set New Password----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def set_new_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == 'POST' and user is not None and default_token_generator.check_token(user, token):
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.is_active = True  # Ensure the user is active
            group = get_object_or_404(Group, name='Author')
            user.groups.add(group)
            user.save()
            logger.info(f'Password successfully set for user: {user.username}')
            return redirect('login')
        else:
            logger.error(f'Form errors: {form.errors}')
    else:
        form = SetPasswordForm(user)
        if user is None:
            logger.error(f'User is None, uidb64: {uidb64}, token: {token}')
        if not default_token_generator.check_token(user, token):
            logger.error(f'Token verification failed, uidb64: {uidb64}, token: {token}')

    context = {
        'form': form,
        'uidb64': uidb64,
        'token': token,
    }

    if uidb64:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
            context['username'] = user.first_name
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            context['username'] = None

    return render(request, 'set_new_password.html', context)



# --------Customer Password Change-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        uidb64 = self.kwargs.get('uidb64')
        if uidb64:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = get_object_or_404(User, pk=uid)
                context['username'] = user.first_name
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                context['username'] = None
                
        
        return context

from django.utils.crypto import get_random_string
def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    form.add_error('email', 'After registration, you should have received a registration success email. Please click "Active My Account" link in that email to activate your account.')
                    return render(request, 'password_reset_form.html', {'form': form})
                
            except User.DoesNotExist:
                form.add_error('email', 'Email address not found.')
                return render(request, 'password_reset_form.html', {'form': form})

            form.save(request=request)
            
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset_form.html', {'form': form})

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('password_change_done')
    
    
# ------Profile Page-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required

def profile(request):
    user = request.user
    try:
        author = Author.objects.get(user=user)
    except Author.DoesNotExist:
        author = None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        author_form = AuthorForm(request.POST, instance=author)

        if user_form.is_valid() and author_form.is_valid():
            user_form.save()
            author_form.save()
            
            # Add the user to the "Author" group if they are not already in it
                
            return redirect('profile')
        else:
            print("User form errors:", user_form.errors)
            print("Author form errors:", author_form.errors)
    else:
        user_form = UserForm(instance=user)
        author_form = AuthorForm(instance=author)

    context = {
        'user_form': user_form,
        'author_form': author_form,
        'author': author,
    }
    return render(request, 'profile.html', context)

def editor_profile(request):
    editor = get_object_or_404(Editor, user=request.user)

    if request.method == 'POST':
        form = EditorProfileForm(request.POST, instance=editor)
        if form.is_valid():
            form.save()
            return redirect('editor_profile')  # Redirect to the same page after saving
    else:
        form = EditorProfileForm(instance=editor)

    return render(request, 'editor_profile.html', {
        'editor': editor,
        'form': form
    })
# -----------------------------------------------------------------------Current Issues----------------------------------------------------------------------------------------------------------------


def current_issue_view(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    journals = Journal.objects.all()

    # Get the latest volume for the journal
    latest_volume = Volume.objects.filter(journal=journal).order_by('-year', '-volume').first()

    if latest_volume:
        # Get the latest issue from the latest volume
        latest_issue = Issue.objects.filter(volume=latest_volume).order_by('-issue').first()
        
        if latest_issue:
            # Get the published articles for the latest issue
            latest_issues = Published_article.objects.filter(issue=latest_issue).order_by('-id')
        else:
            latest_issues = Published_article.objects.none()
    else:
        latest_issues = Published_article.objects.none()
        
    for article in latest_issues:
        accepted_submission = article.accepted_submission
        if accepted_submission and accepted_submission.submission:
            submission = accepted_submission.submission
            co_authors = CoAuthor.objects.filter(submission=submission)
            article.co_authors = co_authors if co_authors.exists() else None
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': accepted_submission.corrected_title,
                'authors': submission.author.user.get_full_name(),
                'file': accepted_submission.typeset_file
            }
        else:
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': article.title,
                'authors': article.author,
                'file': article.file,
            }
        article.article_data = article_data

    return render(request, 'current_issue.html', {'journal': journal, 'latest_issues': latest_issues,'latest_iss': latest_issue, 'latest_volume': latest_volume, 'journals': journals})





def issue_detail_view(request, journal_id, volume_id, issue_id):
    journals = Journal.objects.all()
    journal = get_object_or_404(Journal, pk=journal_id)
    volume = get_object_or_404(Volume, pk=volume_id, journal=journal)
    issue = get_object_or_404(Issue, pk=issue_id, volume=volume)
    articles = Published_article.objects.filter(issue=issue)
    
    
    for article in articles:
        if article.accepted_submission is None:
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': article.title,
                'authors': article.author,
                'file' : article.file,
            }
        else:
            article_data = {
                'volume': article.issue.volume.volume,
                'issue': article.issue.issue,
                'title': article.accepted_submission.corrected_title,
                'authors': article.accepted_submission.submission.author.user.get_full_name(),
                'file' : article.accepted_submission.typeset_file,
            }
        article.article_data = article_data
        
    jcs_journal = Journal.objects.get(title='JCS') 
    latest_volume = Volume.objects.filter(journal=jcs_journal).order_by('-year', '-volume').first()
    if latest_volume:
        # Get the latest issue for the latest volume
        latest_issue = Issue.objects.filter(volume=latest_volume).order_by('-issue').first()
        
    return render(request, 'issue_detail.html', {'journal': journal, 'volume': volume, 'issue': issue, 'articles': articles, 'journals': journals, 'latest_issue':latest_issue})








# ----------------------------------------------------------Archives view----------------------------------------------------------------------------------------------------------------

def archive_view(request, journal_id):

    journal = get_object_or_404(Journal, pk=journal_id)
    journals= Journal.objects.all()
    volumes = Volume.objects.filter(journal=journal).order_by('-id')
    
    jcs_journal = Journal.objects.get(title='JCS') 
    latest_volume = Volume.objects.filter(journal=jcs_journal).order_by('-year', '-volume').first()
    if latest_volume:
        # Get the latest issue for the latest volume
        latest_issue = Issue.objects.filter(volume=latest_volume).order_by('-issue').first()
    
    
    return render(request, 'archives.html', {'journal': journal, 'volumes': volumes, 'journals': journals,'latest_issue':latest_issue})

# def issue_detail_view(request, journal_id, volume_id, issue_id):
#     journals = Journal.objects.all()
#     journal = get_object_or_404(Journal, pk=journal_id)
#     volume = get_object_or_404(Volume, pk=volume_id, journal=journal)
#     issue = get_object_or_404(Issue, pk=issue_id, volume=volume)
#     articles = Published_article.objects.filter(issue=issue)
    
#     return render(request, 'issue_detail.html', {'journal': journal, 'volume': volume, 'issue': issue, 'articles': articles, 'journals': journals})




# -----------------------------Journal Management-------------------------------------------------------------------------------------------------------------------------------------
def add_journal(request):
    if request.method == 'POST':
        form = JournalForm(request.POST)
        if form.is_valid():
            journal = form.save()
            Date.objects.create(
                journal=journal,
                due_days_to_accept_invitation=14,
                due_days_to_review=14,
                due_days_to_minor_revision=14,
                due_days_to_major_revision=14,
                due_days_to_payment=14,
                due_days_to_corrections=14,
                due_days_to_typeset_approval=14,
                due_days_to_next_step=14,
            )
            return redirect('add_journal')  # Redirect to a desired URL after saving
    else:
        form = JournalForm()
    
    return render(request, 'add_journal.html', {'form': form})



# --------Base for users--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def base_view(request):
    user = request.user
    ae_or_eic = user.groups.filter(name__in=['AE', 'EIC']).exists()
    # print("-------------------------------------",ae_or_eic)
    author_or_reviewer = user.groups.filter(name__in=['Author', 'Reviewer']).exists()
    
    context = {
        'ae_or_eic': ae_or_eic,
        'author_or_reviewer': author_or_reviewer,
    }
    return render(request, 'base.html',context)

# download_count
def download_article(request, article_id):
    # Retrieve the article
    article = get_object_or_404(Published_article, id=article_id)

    # Increment the download count
    article.download_count += 1
    article.save()

    # Redirect to the file URL
    if article.file:
        return redirect(article.file.url)
    else:
        # Handle case where the file doesn't exist
        return redirect('index') 
    
#  feedback
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feedback
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback', '').strip()
        if feedback_text:
            Feedback.objects.create(user=request.user, feedback=feedback_text)
            return JsonResponse({
                'status': 'success', 
                'message': 'Feedback submitted successfully.'
            })
        return JsonResponse({
            'status': 'error', 
            'message': 'Feedback cannot be empty.'
        }, status=400)
    return JsonResponse({
        'status': 'error', 
        'message': 'Invalid request method.'
    }, status=405)

def feedback_list(request):
    feedbacks = Feedback.objects.filter(is_active=True).order_by('-submitted_on')
    print("feedbacks",feedbacks)
    return render(request, 'feedback_popup.html', {'feedbacks': feedbacks})

# --Latex 
# import os
# import re
# import glob
# import subprocess
# from django.conf import settings
# from django.http import HttpResponse, FileResponse
# from django.shortcuts import render

# import os
# import subprocess
# import re
# import glob
# from django.http import HttpResponse, FileResponse
# from django.conf import settings
# from django.shortcuts import render

# def convert_docx_to_pdf(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('docx_file')
        
#         # Check if file is uploaded
#         if not uploaded_file:
#             return HttpResponse("No file uploaded.")
        
#         # Check if file is a DOCX
#         if not uploaded_file.name.endswith('.docx'):
#             return HttpResponse("Uploaded file is not a DOCX file.")

#         # Create output directory
#         base_dir = os.path.join(settings.BASE_DIR, 'latex_output')
#         os.makedirs(base_dir, exist_ok=True)

#         # Save uploaded DOCX file
#         docx_path = os.path.join(base_dir, 'input.docx')
#         with open(docx_path, 'wb+') as f:
#             for chunk in uploaded_file.chunks():
#                 f.write(chunk)

#         # Convert DOCX to LaTeX using Pandoc
#         tex_path = os.path.join(base_dir, 'converted.tex')
#         try:
#             subprocess.run(
#                 [
#                     'pandoc', docx_path,
#                     '--from=docx', '--to=latex',
#                     '-s',
#                     '--template=default',
#                     '-o', tex_path
#                 ],
#                 check=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#         except subprocess.CalledProcessError as e:
#             return HttpResponse(f"<h3>Pandoc conversion failed:</h3><pre>{e.stderr.decode()}</pre>")

#         # Clean LaTeX content
#         try:
#             with open(tex_path, 'r', encoding='utf-8') as f:
#                 tex_content = f.read()

#             # Remove problematic macros (from Word styles)
#             tex_content = re.sub(r'\\GTS@[a-zA-Z@]+', '', tex_content)
#             tex_content = re.sub(r'\\fi\b', '', tex_content)
#             tex_content = re.sub(r'\\if[a-zA-Z@]+\b', '', tex_content)

#             # Replace bullet symbols with LaTeX itemize
#             bullet_symbols = ['•', '●', '▪', '■', '']
#             for bullet in bullet_symbols:
#                 tex_content = tex_content.replace(bullet, r'\item ')

#             # Replace special symbols
#             tex_content = tex_content.replace('_', r'\_')
#             tex_content = tex_content.replace('@', r'\@')

#             with open(tex_path, 'w', encoding='utf-8') as f:
#                 f.write(tex_content)

#         except Exception as e:
#             return HttpResponse(f"<h3>Error cleaning LaTeX file:</h3><pre>{str(e)}</pre>")

#         # Compile LaTeX to PDF using xelatex (better support for fonts)
#         try:
#             subprocess.run(
#                 ['xelatex', '-interaction=nonstopmode', 'converted.tex'],
#                 cwd=base_dir,
#                 check=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#         except subprocess.CalledProcessError as e:
#             log_path = os.path.join(base_dir, 'converted.log')
#             if os.path.exists(log_path):
#                 with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
#                     log_content = log_file.read()
#                 return HttpResponse(f"<h3>LaTeX compilation failed. Here's the log:</h3><pre>{log_content[-3000:]}</pre>")
#             else:
#                 return HttpResponse(f"<h3>LaTeX compilation failed:</h3><pre>{e.stderr.decode()}</pre>")

#         # Return the PDF for download
#         pdf_path = os.path.join(base_dir, 'converted.pdf')
#         if os.path.exists(pdf_path):
#             # Optional: cleanup files
#             for file in glob.glob(os.path.join(base_dir, '*')):
#                 if not file.endswith('.pdf'):
#                     os.remove(file)
#             with open(pdf_path, 'rb') as pdf_file:
#                 return FileResponse(pdf_file, as_attachment=True, filename='converted.pdf')

#         return HttpResponse("PDF file was not generated.")

#     # Render form for file upload
#     return render(request, 'upload_docx.html')

import os
from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import subprocess
from .forms import DocumentForm
from .extractors import extract_docx, extract_pdf, extract_pdf_ocr
from .converter import text_to_latex

def upload_file(request):
    """Handle file upload and LaTeX conversion."""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['document']
            # Save the uploaded file temporarily
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            filepath = fs.path(filename)
            
            # Extract text based on file type
            if file.name.endswith('.docx'):
                text = extract_docx(filepath)
            elif file.name.endswith('.pdf'):
                try:
                    text = extract_pdf(filepath)  # Try text extraction first
                except:
                    text = extract_pdf_ocr(filepath)  # Fallback to OCR
            else:
                text = file.read().decode('utf-8')  # For .txt files
            
            # Convert to LaTeX
            latex_code = text_to_latex(text)
            
            # Clean up the temporary file
            os.remove(filepath)
            
            # Render the LaTeX for review
            return render(request, 'review.html', {
                'latex_code': latex_code,
                'filename': file.name
            })
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})

import os
import re
import json
import subprocess
from django.http import JsonResponse, FileResponse
from docx import Document


import re

def sanitize_latex(text):
    """Enhanced LaTeX sanitization with proper structure preservation"""
    
    # Preserve original line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Special character escaping
    replacements = {
        '\\': r'\textbackslash{}',
        '_': r'\_',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '–': '--',  # en-dash
        '—': '---', # em-dash
        '“': r'``',
        '”': r"''",
        '‘': r'`',
        '’': r"'",
    }
    
    for char, escape in replacements.items():
        text = text.replace(char, escape)

    # Fix author blocks and email addresses
    text = re.sub(
        r'([A-Z]\.[A-Za-z]+)(.*?)([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'\\textbf{\1}\2\\texttt{\3}\\newline',
        text
    )
    
    # Preserve section numbering
    text = re.sub(r'^(\d+\.)\s*([A-Z][A-Z\s]+)$', 
                 r'\\section*{\2}', text, flags=re.MULTILINE)
    
    # Handle lists properly
    lines = text.split('\n')
    output = []
    in_itemize = False
    in_enumerate = False
    in_author_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines in author block
        if "Professor" in line or "@" in line:
            if not in_author_block:
                output.append(r'\begin{center}')
                in_author_block = True
            if stripped:
                output.append(line)
            continue
        elif in_author_block:
            output.append(r'\end{center}')
            in_author_block = False
        
        # Numbered lists
        if re.match(r'^\d+\.\s', stripped):
            if not in_enumerate:
                output.append(r'\begin{enumerate}[label=\arabic*.]')
                in_enumerate = True
            content = re.sub(r'^\d+\.\s*', '', stripped)
            output.append(r'\item ' + content)
        
        # Bullet points
        elif re.match(r'^(•|-|)\s+', stripped):
            if not in_itemize:
                output.append(r'\begin{itemize}')
                in_itemize = True
            content = re.sub(r'^(•|-|)\s+', '', stripped)
            output.append(r'\item ' + content)
        
        # Regular text
        else:
            if in_enumerate:
                output.append(r'\end{enumerate}')
                in_enumerate = False
            if in_itemize:
                output.append(r'\end{itemize}')
                in_itemize = False
            
            # Preserve empty lines as paragraph breaks
            if stripped == '':
                output.append(r'\par')
            else:
                # Handle figure references
                line = re.sub(r'Fig(\d+)\.', r'\\textbf{Figure \1}:', line)
                output.append(line)
    
    # Close any open environments
    if in_enumerate:
        output.append(r'\end{enumerate}')
    if in_itemize:
        output.append(r'\end{itemize}')
    if in_author_block:
        output.append(r'\end{center}')
    
    text = '\n'.join(output)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def text_to_latex(text):
    """Professional LaTeX template with proper document structure"""
    latex = sanitize_latex(text)
    
    # Extract author content if it exists
    author_match = re.search(r'\\\\begin\{center\}(.*?)\\\\end\{center\}', latex, re.DOTALL)
    author_content = author_match.group(1) if author_match else ''
    
    # Remove author block from main content
    main_content = re.sub(r'\\\\begin\{center\}.*?\\\\end\{center\}', '', latex, flags=re.DOTALL).strip()
    
    # Build LaTeX document using raw strings and proper escaping
    latex_template = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{enumitem}
\usepackage{parskip}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage[a4paper, total={6in, 8in}]{geometry}

% Custom command for author blocks
\newcommand{\authorblock}[3]{
\textbf{#1} \\ #2 \\ \texttt{#3}
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{1em}
\setlist[itemize]{leftmargin=*,nosep}
\setlist[enumerate]{leftmargin=*}

\title{Towards Transparent Phishing Email Detection: A Transformer-Based Explainable AI Approach}
\author{
\begin{center}
""" + author_content + r"""
\end{center}
}
\date{}

\begin{document}

\maketitle

""" + main_content + r"""

\end{document}"""
    
    return latex_template

def compile_pdf(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latex_code = data.get('latex', '')
            
            if not latex_code:
                return JsonResponse({'error': 'No LaTeX code provided'}, status=400)

            output_dir = 'latex_output'
            os.makedirs(output_dir, exist_ok=True)
            
            tex_path = os.path.join(output_dir, 'output.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            try:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 
                     '-output-directory', output_dir, tex_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                pdf_path = os.path.join(output_dir, 'output.pdf')
                
                if os.path.exists(pdf_path):
                    response = FileResponse(
                        open(pdf_path, 'rb'),
                        content_type='application/pdf'
                    )
                    response['Content-Disposition'] = 'inline; filename="converted.pdf"'
                    return response
                else:
                    error_msg = result.stderr or "PDF generation failed"
                    return JsonResponse({'error': error_msg}, status=500)
                    
            except subprocess.TimeoutExpired:
                return JsonResponse({'error': 'PDF generation timed out'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)