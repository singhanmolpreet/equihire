from django.db import models

class Expert(models.Model):
    name = models.CharField(max_length=100)
    expertise = models.TextField(help_text="Comma-separated list of expert's areas of expertise")

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    expertise = models.TextField(help_text="Comma-separated list of candidate's areas of expertise")

    def __str__(self):
        return self.name

class Score(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    relevancy_score = models.FloatField()

    def __str__(self):
        return f"{self.expert.name} - {self.candidate.name} ({self.relevancy_score})"
