from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import JobPostingForm
from .models import JobPosting
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from authentication_usertype.models import CompanyProfile, ExpertAssignment
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.sites.shortcuts import get_current_site
import uuid  # Import uuid



User = get_user_model()  #  Get your CustomUser model

def is_company_user(user):
    return user.role == 'COMPANY'

@login_required
@user_passes_test(is_company_user, login_url='home')  # Redirect to 'home' for non-company users
def company_dashboard(request):
    """
    View for the company dashboard, showing the company's job postings.
    """
    #  Use select_related to optimize database queries.
    job_postings = JobPosting.objects.filter(company=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(job_postings, 10)  # Show 10 job postings per page
    page = request.GET.get('page')
    try:
        job_postings_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        job_postings_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        job_postings_page = paginator.page(paginator.num_pages)
    context = {
        'job_postings': job_postings_page,
    }
    return render(request, 'job_postings/company_dashboard.html', context)



@login_required
@user_passes_test(is_company_user, login_url='home')  # Redirect to 'home' for non-company users
def add_job_posting(request):
    """
    View for adding a new job posting.
    """
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = request.user  # Set the company
            job_posting.save()
            messages.success(request, "Job posting added successfully!")
            return redirect('job_postings:company_dashboard')
        else:
            messages.error(request, "There was an error in the form. Please correct it.")
            #  Include the form in the context to display errors
            return render(request, 'job_postings/add_job_posting.html', {'form': form})
    else:
        form = JobPostingForm()  # Instantiate the form for a GET request
    return render(request, 'job_postings/add_job_posting.html', {'form': form})


@login_required
@user_passes_test(is_company_user, login_url='home')
def edit_job_posting(request, job_posting_id):
    """
    View for editing an existing job posting.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id, company=request.user)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posting updated successfully!")
            return redirect('job_postings:company_dashboard')
        else:
            messages.error(request, "There was an error in the form. Please correct it.")
            return render(request, 'job_postings/edit_job_posting.html', {'form': form, 'job_posting': job_posting})
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'job_postings/edit_job_posting.html', {'form': form, 'job_posting': job_posting})


@login_required
@user_passes_test(is_company_user, login_url='home')
def delete_job_posting(request, job_posting_id):
    """
    View for deleting a job posting.  Added security check.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id, company=request.user)
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, "Job posting deleted successfully!")
        return redirect('job_postings:company_dashboard')
    #  Add a template to confirm deletion
    return render(request, 'job_postings/delete_job_posting_confirm.html', {'job_posting': job_posting})
