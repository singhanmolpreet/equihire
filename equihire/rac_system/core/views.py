import csv
from django.shortcuts import render
from .models import Expert, Candidate, Score
from .forms import UploadCSVForm
from io import TextIOWrapper
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from fpdf import FPDF
from django.contrib.auth.decorators import login_required

# Home Page
def home(request):
    return render(request, 'core/home.html')


def calculate_relevancy(expert_expertise, candidate_expertise):
    # Handle empty expertise fields
    expert_expertise = expert_expertise.strip()
    candidate_expertise = candidate_expertise.strip()

    if not expert_expertise or not candidate_expertise:
        return 0

    # Create sets of skills
    expert_skills = set(skill.strip() for skill in expert_expertise.split(","))
    candidate_skills = set(skill.strip() for skill in candidate_expertise.split(","))
    
    # Calculate common skills and total unique skills
    common_skills = expert_skills.intersection(candidate_skills)
    total_unique_skills = expert_skills.union(candidate_skills)

    # Calculate relevancy score
    if len(total_unique_skills) == 0:  # No skills at all
        return 0
    
    relevancy_score = (len(common_skills) / len(total_unique_skills)) * 10  # Score out of 10
    return relevancy_score

@login_required(login_url='login')
def upload_and_match(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            expert_csv = request.FILES['expert_csv']
            candidate_csv = request.FILES['candidate_csv']

            # Clear old records
            Expert.objects.all().delete()
            Candidate.objects.all().delete()
            Score.objects.all().delete()

            # Read and save experts
            experts = []
            expert_file = TextIOWrapper(expert_csv.file, encoding='utf-8')
            reader = csv.DictReader(expert_file)
            for row in reader:
                expert = Expert.objects.create(
                    name=row['name'],
                    expertise=row['expertise']
                )
                experts.append(expert)

            # Read and save candidates
            candidates = []
            candidate_file = TextIOWrapper(candidate_csv.file, encoding='utf-8')
            reader = csv.DictReader(candidate_file)
            for row in reader:
                candidate = Candidate.objects.create(
                    name=row['name'],
                    expertise=row['expertise']
                )
                candidates.append(candidate)

            # Match candidates with experts
            for candidate in candidates:
                best_expert = None
                best_score = 0
                for expert in experts:
                    relevancy_score = calculate_relevancy(expert.expertise, candidate.expertise)
                    if relevancy_score > best_score:  # Assign only if current score is better
                        best_score = relevancy_score
                        best_expert = expert
                # Save the best match
                Score.objects.create(expert=best_expert, candidate=candidate, relevancy_score=best_score)

            return render(request, 'core/results.html', {'scores': Score.objects.all()})
    else:
        form = UploadCSVForm()

    return render(request, 'core/upload.html', {'form': form})

@login_required(login_url='login')
def download_pdf(request):
    # Query all scores for the PDF
    scores = Score.objects.all()

    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add a title
    pdf.cell(200, 10, txt="Interview Assignments", ln=True, align='C')

    # Add header for the table
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(60, 10, 'Expert', 1)
    pdf.cell(60, 10, 'Candidate', 1)
    pdf.cell(60, 10, 'Relevancy Score', 1)
    pdf.ln()

    # Add data to the table
    pdf.set_font("Arial", size=12)
    for score in scores:
        pdf.cell(60, 10, score.expert.name, 1)
        pdf.cell(60, 10, score.candidate.name, 1)
        pdf.cell(60, 10, f"{score.relevancy_score:.2f}", 1)
        pdf.ln()

    # Set the response
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="interview_assignments.pdf"'
    return response


