from django.db import models
from django.contrib.auth.models import User

class Title(models.Model):
    title = models.CharField(max_length=25,null = False)

    def __str__(self):
        return self.title
    
class Country(models.Model):
    country = models.CharField(max_length=100,null = False)
    code = models.CharField(max_length=3,null = False)
    ph_code = models.CharField(max_length=3,null = False)

    def __str__(self):
        return self.country

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=10)
    orcid_id = models.CharField(max_length=19)
    scopus_id = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_reviewer = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Editor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affliation = models.CharField(max_length=255) 
    mobile_number = models.CharField(max_length=25)
    is_active = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.affliation


# Create your models here.