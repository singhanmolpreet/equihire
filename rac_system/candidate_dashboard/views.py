from company_dashboard.models import JobPosting  # Import JobPosting
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from company_dashboard.models import JobPosting
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication_usertype.models import CandidateProfile  # Import your models
from django.contrib.auth import get_user_model


from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist 





User = get_user_model()  #  Get your CustomUser model

def is_candidate_user(user):
    return user.role == 'CANDIDATE'


@login_required(login_url='login')
@user_passes_test(is_candidate_user, login_url='home')
def dashboard(request):
    """
    View for the candidate dashboard.  Displays relevant information to a candidate.
    """
    try:
        candidate_profile = request.user.candidate_profile
    except AttributeError:
        return render(request, 'candidate_dashboard/dashboard.html', {'no_profile': True})

    # Get the jobs the candidate has applied for.
    applications = candidate_profile.applied_jobs.all()

    # Get recommended jobs
    recommended_jobs = JobPosting.objects.exclude(id__in=candidate_profile.applied_jobs.values_list('id', flat=True)).order_by('-created_at')

    # Pagination
    paginator = Paginator(recommended_jobs, 5)
    page = request.GET.get('page')
    try:
        recommended_jobs_page = paginator.page(page)
    except PageNotAnInteger:
        recommended_jobs_page = paginator.page(1)
    except EmptyPage:
        recommended_jobs_page = paginator.page(paginator.num_pages)

    context = {
        'candidate_profile': candidate_profile,
        'applications': applications,
        'recommended_jobs': recommended_jobs_page,
    }
    return render(request, 'candidate_dashboard/dashboard.html', context)



@login_required(login_url='login')
@user_passes_test(is_candidate_user, login_url='home')
def job_listings(request):
    """
    View to display all job listings for candidates.
    """
    job_postings = JobPosting.objects.all().order_by('-created_at')

    paginator = Paginator(job_postings, 10)
    page = request.GET.get('page')
    try:
        job_postings_page = paginator.page(page)
    except PageNotAnInteger:
        job_postings_page = paginator.page(1)
    except EmptyPage:
        job_postings_page = paginator.page(paginator.num_pages)

    return render(request, 'candidate_dashboard/job_listings.html', {'job_postings': job_postings_page})


@login_required
@user_passes_test(is_candidate_user, login_url='home')
def job_detail(request, job_posting_id):
    """View to display the details of a single job posting."""
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    return render(request, 'candidate_dashboard/job_detail.html', {'job_posting': job_posting})



@login_required(login_url='login')
@user_passes_test(is_candidate_user, login_url='home')
def apply_for_job(request, job_posting_id):
    """View to handle a candidate applying for a job."""
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)

    try:
        candidate_profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist: # Change this line
        # Handle the case where the user doesn't have a CandidateProfile.
        # You might want to redirect them to a profile creation page or show a message.
        return redirect('register')  # Create this template

    if request.method == 'POST':
        # Handle the application:
        # 1. Add the job to the candidate's applied_jobs ManyToManyField.
        candidate_profile.applied_jobs.add(job_posting)
        # 2. Redirect to a confirmation page.
        return redirect('candidate_dashboard:application_confirmation', job_posting_id=job_posting.id)  # Create this URL and template

    # 3.  If it's a GET request, show the "are you sure?" page.
    return render(request, 'candidate_dashboard/apply_for_job.html', {'job_posting': job_posting})


@login_required(login_url='login')
@user_passes_test(is_candidate_user, login_url='home')
def application_confirmation(request, job_posting_id):
    """
    View to display a confirmation message after a candidate applies for a job.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    return render(request, 'candidate_dashboard/application_confirmation.html', {'job_posting': job_posting})

