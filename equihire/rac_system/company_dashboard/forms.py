from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    """
    Form for creating and updating job postings.
    """
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'required_skills', 'minimum_experience', 'minimum_salary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 60, 'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={'rows': 2, 'cols': 60, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }
        labels = {
            'title': 'Job Title',
            'description': 'Job Description',
            'required_skills': 'Required Skills',
            'minimum_experience': 'Minimum Experience (Years)',
        }

