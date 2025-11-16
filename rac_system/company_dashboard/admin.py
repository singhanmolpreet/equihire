from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import JobPosting

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'company')
    search_fields = ('title', 'description', 'required_skills', 'company__username', 'company__email')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('company', 'title', 'description')
        }),
        ('Requirements', {
            'fields': ('required_skills', 'minimum_experience')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')