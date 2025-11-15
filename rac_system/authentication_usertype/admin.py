from django.contrib import admin
from .models import CustomUser, CandidateProfile, CompanyProfile, ExpertAssignment

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience', 'is_expert', 'company')
    search_fields = ('user__email', 'expertise')

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'gstin', 'user')
    search_fields = ('company_name', 'gstin')

@admin.register(ExpertAssignment)
class ExpertAssignmentAdmin(admin.ModelAdmin):
    list_display = ('expert', 'company', 'job_posting', 'created_at')
    search_fields = ('expert__user__email', 'job_posting')
