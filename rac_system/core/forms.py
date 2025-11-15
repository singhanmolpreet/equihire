from django import forms

class UploadCSVForm(forms.Form):
    expert_csv = forms.FileField(label="Upload Expert CSV")
    candidate_csv = forms.FileField(label="Upload Candidate CSV")
    
class CandidateForm(forms.Form):
    name = forms.CharField(max_length = 200, label="name")
    expertise = forms.CharField(label='expertise')

class ExpertiseForm(forms.Form):
    name = forms.CharField(max_length = 200, label="name")
    expertise = forms.CharField(label='expertise')