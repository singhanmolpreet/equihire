from django import forms
from .models import CustomUser, CandidateProfile, CompanyProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'role', 'password']

class CandidateExtraForm(forms.ModelForm):
    experience = forms.IntegerField(
        min_value=0,  # Minimum value to ensure no negative values
        label="Experience (in months)",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter experience in months'}),
    )
    
    class Meta:
        model = CandidateProfile
        fields = ['experience', 'expertise', 'image']

class CompanyExtraForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'address', 'description', 'image', 'gstin']
