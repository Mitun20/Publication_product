# dl/models
from django.db import models
from oss.models import Journal, Accepted_Submission

# Create your models here.


class Volume(models.Model):
    volume = models.IntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField()
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.volume)

class Issue(models.Model):
    issue = models.IntegerField()
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)
    description = models.CharField(max_length=255 ,verbose_name="Month")
    

    def __str__(self):
        return str(self.issue)


class Published_article(models.Model):
    accepted_submission = models.ForeignKey(Accepted_Submission, on_delete=models.CASCADE, null=True, blank=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    published_on_date = models.DateField()
    doi = models.CharField(max_length=255)
    download_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)

    def __str__(self):
        return str(self.accepted_submission.corrected_title) if self.accepted_submission else str(self.title)
