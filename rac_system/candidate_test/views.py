from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from django.db.models import Sum

from .models import Test, Question, Choice, CandidateTestAttempt, CandidateAnswer
from company_dashboard.models import JobPosting
from authentication_usertype.models import CandidateProfile
from .forms import TestForm, QuestionFormSet

# Helper function to check if the user is a candidate
def is_candidate(user):
    return user.is_authenticated and hasattr(user, 'candidate_profile') and user.role == 'CANDIDATE'

# --- Company Views ---

# assessment/views.py - modified create_test

def create_test(request):
    """
    Handles the creation of a Test and checks for job_id GET parameter to pre-select job.
    """
    if not request.user.is_authenticated or request.user.role != 'COMPANY':
        messages.error(request, "Permission denied. Only companies can create tests.")
        return redirect('home')

    initial_data = {}
    job_id = request.GET.get('job_id')
    if job_id:
        # Check if the job_id belongs to the current company before setting initial data
        try:
            job_post = JobPosting.objects.get(pk=job_id, company=request.user)
            initial_data['job_post'] = job_post.id
        except JobPosting.DoesNotExist:
            messages.warning(request, "The specified job posting ID is invalid or does not belong to you.")
    
    if request.method == 'POST':
        # The job_id will be in request.POST if the hidden field is set, or form handles it
        test_form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')

        if test_form.is_valid() and question_formset.is_valid():
            # ... (rest of your existing successful submission logic) ...
            try:
                with transaction.atomic():
                    # Save logic remains the same
                    test_instance = test_form.save()
                    question_instances = question_formset.save(commit=False)

                    for i, question in enumerate(question_instances):
                        question.test = test_instance
                        question.save()

                        question_prefix = f'questions-{i}'
                        correct_choice_index = request.POST.get(f'{question_prefix}-correct_choice')

                        for j in range(1, 5):
                            choice_text_key = f'{question_prefix}-choice_{j}'
                            choice_text = request.POST.get(choice_text_key)

                            if choice_text:
                                is_correct = (correct_choice_index == str(j))
                                Choice.objects.create(
                                    question=question,
                                    text=choice_text,
                                    is_correct=is_correct
                                )
                    
                    question_formset.save_m2m()
                    
                    messages.success(request, f'Test "{test_instance.title}" and its questions were successfully created and linked to the job!')
                    return redirect('test_success', test_id=test_instance.id)

            except Exception as e:
                messages.error(request, f"An error occurred during test creation: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        # On GET request, pass initial_data to pre-select the job
        test_form = TestForm(initial=initial_data) 
        question_formset = QuestionFormSet(prefix='questions')
        
    context = {
        'test_form': test_form,
        'question_formset': question_formset,
    }
    return render(request, 'assessment/create_test.html', context)

def test_success(request, test_id):
    """Simple success page to show the newly created test."""
    test = get_object_or_404(Test, pk=test_id)
    return render(request, 'assessment/test_success.html', {'test': test})

# --- Candidate Views ---

def take_test(request, test_id):
    """Allows a candidate to start and submit a test attempt."""
    if not is_candidate(request.user):
        messages.error(request, "Access denied. You must be logged in as a candidate to take tests.")
        return redirect('login')

    candidate_profile = request.user.candidate_profile
    test = get_object_or_404(Test, pk=test_id)

    # 1. Get or Create Attempt
    try:
        attempt, created = CandidateTestAttempt.objects.get_or_create(
            candidate=candidate_profile,
            test=test,
            is_completed=False,
            defaults={'job_post': test.job_post} 
        )
    except Exception:
        attempt = CandidateTestAttempt.objects.filter(candidate=candidate_profile, test=test).order_by('-start_time').first()
        if not attempt:
            raise Http404("Could not initialize test attempt.")

    # Check if the user has already completed the test
    if attempt.is_completed:
        messages.info(request, "You have already completed this test.")
        return redirect('test_results', attempt_id=attempt.id)
    
    questions = test.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        total_score = 0
        
        try:
            with transaction.atomic():
                # Clear previous answers if the user somehow submits twice without refreshing
                CandidateAnswer.objects.filter(attempt=attempt).delete()
                
                # 2. Process Submitted Answers
                for question in questions:
                    selected_choice_id = request.POST.get(f'question_{question.id}')

                    selected_choice = None
                    is_correct = False

                    if selected_choice_id:
                        try:
                            selected_choice = Choice.objects.get(pk=selected_choice_id, question=question)
                            if selected_choice.is_correct:
                                is_correct = True
                                total_score += question.points
                        except Choice.DoesNotExist:
                            pass 

                    CandidateAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=is_correct
                    )
                
                # 3. Finalize Attempt
                attempt.score = total_score
                attempt.end_time = timezone.now()
                attempt.is_completed = True
                attempt.save()

                messages.success(request, f"Test submitted successfully! Your score: {total_score} points.")
                return redirect('test_results', attempt_id=attempt.id)

        except Exception as e:
            messages.error(request, f"An error occurred while submitting the test: {e}")

    # GET request or POST failure
    context = {
        'test': test,
        'questions': questions,
        'attempt': attempt,
        'total_questions': questions.count(),
    }
    return render(request, 'assessment/take_test.html', context)


def test_results(request, attempt_id):
    """Displays the results and score for a completed test attempt."""
    attempt = get_object_or_404(
        CandidateTestAttempt.objects.select_related('candidate__user', 'test'), 
        pk=attempt_id
    )

    # Security check
    if not is_candidate(request.user) or attempt.candidate != request.user.candidate_profile:
        messages.error(request, "Permission denied. You cannot view this result.")
        return redirect('home')

    if not attempt.is_completed:
        messages.warning(request, "This test attempt is not yet completed.")
        return redirect('take_test', test_id=attempt.test.id)

    # Fetch answers for review
    answers = CandidateAnswer.objects.filter(attempt=attempt).select_related(
        'question', 
        'selected_choice'
    ).order_by('question__id')
    
    total_possible_score = attempt.test.questions.aggregate(total=Sum('points'))['total'] or 0
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'total_possible_score': total_possible_score,
        'score_percentage': (attempt.score / total_possible_score * 100) if total_possible_score else 0,
    }
    return render(request, 'assessment/test_results.html', context)