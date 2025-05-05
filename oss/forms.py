from django import forms
from .models import * 


class CorrectedFileForm(forms.Form):
    submission_id = forms.IntegerField()
    corrected_file = forms.FileField()
    corrected_title = forms.CharField(max_length=255, required=True)
    corrected_abstract = forms.CharField(widget=forms.Textarea, required=True)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class SubmissionStepOneForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['article_type', 'title', 'category', 'journal', 'abstract']
        widgets = {
            'article_type': forms.RadioSelect(),
            'category': forms.Select(),
            'journals': forms.Select(),
        }


class CoAuthorForm(forms.ModelForm):
    class Meta:
        model = CoAuthor
        fields = ['name', 'email', 'institution'] 

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)
        for field in ['name', 'email', 'institution']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CoAuthor.objects.filter(email=email, submission=self.submission).exists():
            raise forms.ValidationError("A co-author with this email already exists.")
        return email

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            'cover_letter', 'is_funded', 'no_of_figures', 'no_of_tables', 
            'no_of_words', 'is_submitted_already', 'acknowledgement_1', 
            'acknowledgement_2', 'acknowledgement_3', 'conflict_of_interest', 'coi_describe'
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your cover letter...'}),
        }

    is_funded = forms.TypedChoiceField(
        choices=((0, 'No'), (1, 'Yes')),
        coerce=lambda x: bool(int(x)),
        required=True,
    )
    
    is_submitted_already = forms.TypedChoiceField(
        choices=((0, 'No'), (1, 'Yes')),
        coerce=lambda x: bool(int(x)),
        required=True
    )
    
    conflict_of_interest = forms.TypedChoiceField(
        choices=((0, 'No'), (1, 'Yes')),
        coerce=lambda x: bool(int(x)),
        required=True
    )

    def clean_is_funded(self):
        is_funded = self.cleaned_data.get('is_funded')
        return is_funded
    
    def clean_is_submitted_already(self):
        is_submitted_already = self.cleaned_data.get('is_submitted_already')
        return is_submitted_already
    
    def clean_conflict_of_interest(self):
        conflict_of_interest = self.cleaned_data.get('conflict_of_interest')
        return conflict_of_interest

class FunderForm(forms.ModelForm):
    class Meta:
        model = Funder
        fields = ['detail']
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(FunderForm, self).__init__(*args, **kwargs)
        self.fields['detail'].required = False


class ReviewSubmitForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'disabled': True})
    )

    abstract = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'disabled': True}),
        required=False
    )

    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'disabled': True}),
        required=False
    )

    is_funded = forms.ChoiceField(
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
        required=True
    )

    figures = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'disabled': True}))
    tables = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'disabled': True}))
    words = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'disabled': True}))
    
    is_submitted_already = forms.ChoiceField(
        choices=((1, 'Yes'), (0, 'No')),
        widget=forms.RadioSelect,
        required=True
    )

    acknowledgement_1 = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'disabled': True}))
    acknowledgement_2 = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'disabled': True}))
    acknowledgement_3 = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'disabled': True}))

    conflict_of_interest = forms.ChoiceField(
        choices=[(1, 'Yes'), (0, 'No')],
        widget=forms.RadioSelect,
        required=True
    )

    coi_describe = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'disabled': True}),
        required=False
    )

class KeywordForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ['keyword']


#**********************************************************************************************************

class CustomClearableFileInput(forms.ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.input_type = 'file'

    def render(self, name, value, attrs=None, renderer=None):
        attrs['multiple'] = True
        return super().render(name, value, attrs, renderer)

class SubmissionFileForm(forms.ModelForm):
    # Dynamically fetch the choices from the File_Category model
    file_category = forms.ModelChoiceField(
        queryset=File_Category.objects.all(),
        required=True,
        label='File Category'
    )

    class Meta:
        model = Submission_Files
        fields = ['file', 'file_category']  # Remove 'submission' from fields, as it's set in the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['multiple'] = True  # Allow multiple file selection

    def clean(self):
        cleaned_data = super().clean()
        files = self.files.getlist('file')

        if not files:
            raise forms.ValidationError("You must upload at least one file.")
        
        return cleaned_data
    
# contact form

# forms.py
class ContactForm(forms.Form):
    to_email = forms.EmailField(label='To', max_length=100, help_text='Recipient email address')
    subject = forms.CharField(max_length=100, label='Subject')
    message = forms.CharField(widget=forms.Textarea, label='Message')

    def __init__(self, *args, **kwargs):
        # Accept 'to_email' as an initial value
        to_email = kwargs.pop('to_email', None)
        super(ContactForm, self).__init__(*args, **kwargs)
        if to_email:
            self.fields['to_email'].initial = to_email
            self.fields['to_email'].widget.attrs['readonly'] = True  # Make the field readonly
