from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
 
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
    expert = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    job_posting = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.expert.user.name} is assigned to {self.job_posting}"
    