from django import forms
from django.forms.models import inlineformset_factory
from .models import Test, Question

class TestForm(forms.ModelForm):
    """Form for creating or editing the main Test details."""
    class Meta:
        model = Test
        fields = ['job_post', 'title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'job_post': forms.Select(attrs={'class': 'form-control'}),
        }

QuestionFormSet = inlineformset_factory(
    parent_model=Test,
    model=Question,
    fields=('text', 'points',),
    extra=3,
    can_delete=True,
    widgets={
        'text': forms.Textarea(attrs={'class': 'form-control question-text', 'rows': 2, 'placeholder': 'Enter the question text'}),
        'points': forms.NumberInput(attrs={'class': 'form-control points-input', 'min': 1}),
    }
)