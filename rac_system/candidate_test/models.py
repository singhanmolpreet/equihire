from django.db import models
from company_dashboard.models import JobPosting
from authentication_usertype.models import CandidateProfile # Import existing model

# --- Test Definition Models ---

class Test(models.Model):
    """Represents a set of questions linked to a job post."""
    job_post = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='tests', null=True, blank=True)
    title = models.CharField(max_length=255, help_text="e.g., Python Proficiency Test, Marketing Fundamentals")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    """A single question belonging to a Test."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"Q: {self.text[:50]}..."

class Choice(models.Model):
    """A possible answer choice for a Question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice for Q{self.question.id}: {self.text[:30]} ({'Correct' if self.is_correct else 'Incorrect'})"
    
# --- Models for Tracking Candidate Attempts and Answers ---

class CandidateTestAttempt(models.Model):
    """Tracks a candidate's attempt at taking a specific test."""
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, help_text="Final score in points earned")
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('candidate', 'test') 

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.candidate.user.name}'s attempt on '{self.test.title}' ({status})"

class CandidateAnswer(models.Model):
    """Stores the candidate's selected choice for a specific question in an attempt."""
    attempt = models.ForeignKey(CandidateTestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True) 
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('attempt', 'question') 

    def __str__(self):
        correctness = "Correct" if self.is_correct else "Incorrect/Unanswered"
        return f"Attempt {self.attempt.id}: Q {self.question.id} ({correctness})"