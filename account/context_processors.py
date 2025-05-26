from django.contrib.auth.models import User, Group

def feedback_context(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Author').exists():
        # Get all superusers (treated as Admins)
        admin_users = User.objects.filter(is_superuser=True)

        # Get all users in Reviewer group
        try:
            reviewer_group = Group.objects.get(name='Reviewer')
            reviewers = User.objects.filter(groups=reviewer_group)
        except Group.DoesNotExist:
            reviewers = User.objects.none()

        # Combine both user querysets
        feedback_users = (admin_users | reviewers).distinct()
    if request.user.is_authenticated and request.user.groups.filter(name='Reviewer').exists():
        # Get all superusers (treated as Admins)
        admin_users = User.objects.filter(is_superuser=True)
        feedback_users = (admin_users).distinct()
        
        return {'feedback_users': feedback_users}

    return {}
