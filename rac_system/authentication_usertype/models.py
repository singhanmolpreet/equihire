from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if 'role' not in extra_fields or not extra_fields['role']:
            extra_fields.setdefault('role', 'CANDIDATE')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('CANDIDATE', 'Candidate'),
        ('COMPANY', 'Company'),
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']    
    def __str__(self):
        return self.email
    
class CandidateProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidate_profile')
    experience = models.IntegerField(null=True, blank=True)
    expertise = models.TextField(null=True, blank=True)
    resume_link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='candidate_images/', null=True, blank=True)
    company = models.CharField(max_length=250, null=True, blank=True)
    is_expert = models.BooleanField(default=False)
    applied_jobs = models.ManyToManyField('company_dashboard.JobPosting', related_name='candidates_applied', blank=True)
    
    def __str__(self):
        return self.user.email
    
class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=250)
    address = models.TextField()
    description = models.TextField()
    #type_of_business 
    image = models.ImageField(upload_to='company_images/', null=True, blank=True)
    gstin = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return self.user.email

class ExpertAssignment(models.Model):
    """
    Tracks an invitation sent by a Company to an Expert (via email) 
    to review a specific Job Posting.
    """
    # Links to the job posting being reviewed
    job_posting = models.ForeignKey(
        'company_dashboard.JobPosting',  
        on_delete=models.CASCADE,
        related_name='expert_assignments',
        verbose_name="Job Posting"
    )

    # The company (user) that sent the invitation
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expert_invitations_sent',
        limit_choices_to={'role': 'COMPANY'},
        verbose_name="Assigning Company"
    )

    # The email address of the invited expert (used before they register)
    expert_email = models.EmailField(
        max_length=254,
        verbose_name="Expert's Email",
        null=True,     # <-- ADDED: Allows null in the database
        blank=True     # <-- ADDED: Allows blank in forms/admin
    )

    # The unique token for the invitation link
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Invitation Token"
    )

    # The User object if the expert successfully signed up and claimed the assignment
    assigned_expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expert_reviews',
        limit_choices_to={'role': 'EXPERT'},
        verbose_name="Assigned Expert User"
    )

    # Status of the invitation/assignment
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this invitation/assignment is still valid."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expert Assignment"
        verbose_name_plural = "Expert Assignments"
        # Ensure a company only invites a specific email once per job posting
        unique_together = ('job_posting', 'expert_email')

    def __str__(self):
        return f"Expert assignment for {self.job_posting.title} to {self.expert_email}"