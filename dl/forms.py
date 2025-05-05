from django import forms
from .models import Issue
from oss.models import Article_Status

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['issue', 'volume', 'description']

class SubmissionStatusForm(forms.Form):
    submission_id = forms.IntegerField(widget=forms.HiddenInput())
    article_status = forms.ModelChoiceField(queryset=Article_Status.objects.all())

