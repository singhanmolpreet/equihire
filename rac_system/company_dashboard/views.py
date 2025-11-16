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
# Assuming 'authentication_usertype' is the correct app name where these models reside
from authentication_usertype.models import CompanyProfile, ExpertAssignment 
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.sites.shortcuts import get_current_site
import uuid  # Import uuid



User = get_user_model()  # Get your CustomUser model

def is_company_user(user):
    return user.role == 'COMPANY'

@login_required
@user_passes_test(is_company_user, login_url='home')  # Redirect to 'home' for non-company users
def company_dashboard(request):
    """
    View for the company dashboard, showing the company's job postings.
    (No changes here)
    """
    # Use select_related to optimize database queries.
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
    Redirects to the create_test view upon successful posting.
    """
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = request.user  # Set the company
            job_posting.save()
            messages.success(request, "Job posting added successfully! Now, add an assessment test.")
            
            # --- NEW REDIRECTION LOGIC ---
            # Redirect to the assessment app's test creation view
            # We pass the job_posting ID in the URL, but the assessment form needs to handle it.
            # Since the `create_test` view doesn't currently accept a job ID in its URL, 
            # we will redirect there and rely on the next update.
            # *However, to make the next step easier, let's use a GET parameter now.*
            
            # Option 1: Redirect to a URL with the job ID (recommended)
            # Assuming 'create_test' is in the assessment app (assessment:create_test)
            return redirect(reverse('create_test') + f'?job_id={job_posting.id}')
            
            # Option 2 (If you prefer the original dashboard redirect):
            # return redirect('job_postings:company_dashboard')

        else:
            messages.error(request, "There was an error in the form. Please correct it.")
            return render(request, 'job_postings/add_job_posting.html', {'form': form})
    else:
        form = JobPostingForm()
    return render(request, 'job_postings/add_job_posting.html', {'form': form})


@login_required
@user_passes_test(is_company_user, login_url='home')
def edit_job_posting(request, job_posting_id):
    """
    View for editing an existing job posting.
    (No changes here)
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
    View for deleting a job posting. Added security check.
    (No changes here)
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id, company=request.user)
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, "Job posting deleted successfully!")
        return redirect('job_postings:company_dashboard')
    # Add a template to confirm deletion
    return render(request, 'job_postings/delete_job_posting_confirm.html', {'job_posting': job_posting})
@login_required
@user_passes_test(is_company_user, login_url='home')
def assign_expert_by_email(request, job_posting_id):
    """
    View to assign an expert by sending them a unique tokenized invitation email.
    """
    # Ensure the job posting belongs to the current company user
    job_posting = get_object_or_404(JobPosting, id=job_posting_id, company=request.user)

    if request.method == 'POST':
        expert_email = request.POST.get('expert_email', '').strip()

        if not expert_email:
            messages.error(request, "Please provide a valid expert email address.")
            return redirect('job_postings:company_dashboard') 
        
        # 1. Generate unique token and necessary details
        token = str(uuid.uuid4())
        current_site = get_current_site(request)
        
        # 2. Create the ExpertAssignment record
        try:
            # Check if an assignment already exists for this email/job and update it if so
            assignment, created = ExpertAssignment.objects.update_or_create(
                job_posting=job_posting,
                expert_email=expert_email,
                defaults={
                    'company': request.user,
                    'token': token,
                    'is_active': True
                }
            )
            
        except Exception as e:
            messages.error(request, f"Failed to save assignment record: {e}")
            return redirect('job_postings:company_dashboard')
            
        # 3. Create the invitation URL
        invite_link = request.build_absolute_uri(
            reverse('expert_signup', kwargs={'token': token})
        )
        
        # 4. Prepare and send email
        try:
            # Safely attempt to get company name
            company_name = request.user.companyprofile.company_name
        except:
            company_name = request.user.email

        context = {
            'job_title': job_posting.title,
            'company_name': company_name,
            'invite_link': invite_link,
            'domain': current_site.domain,
            'expert_email': expert_email,
        }
        
        email_html_message = render_to_string('job_postings/expert_invite_email.html', context)
        email_plain_message = f"You have been invited to review applications for the job: {job_posting.title}. Click the link to sign up: {invite_link}"

        try:
            send_mail(
                subject=f'Expert Invitation: Review applications for {job_posting.title}',
                message=email_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[expert_email],
                html_message=email_html_message,
                fail_silently=False,
            )
            if created:
                messages.success(request, f"New invitation sent successfully to {expert_email}!")
            else:
                messages.info(request, f"Re-sent invitation to {expert_email}. The previous token was updated.")
        except Exception as e:
            messages.error(request, f"Invitation record saved, but email sending failed. Check your Django EMAIL settings. Error: {e}")

        return redirect('job_postings:company_dashboard')
    
    return redirect('job_postings:company_dashboard')