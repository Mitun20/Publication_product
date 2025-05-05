from django.contrib.auth.models import Group

def is_ae(user):
    return user.groups.filter(name="AE").exists()

def is_eic(user):
    return user.groups.filter(name='EIC').exists()
        
def is_author(user):
    return user.groups.filter(name='Author').exists()
        
def is_reviewer(user):
    return user.groups.filter(name='Reviewer').exists()

def is_admin_office(user):
    return user.groups.filter(name='Admin Office').exists()

def is_super_admin(user):
    return user.is_superuser
