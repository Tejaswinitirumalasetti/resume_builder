from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from .models import Resume, Skill, Education, Experience, Certification, Project

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,HRFlowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch



# =========================
# Register
# =========================
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')


# =========================
# Login
# =========================
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


# =========================
# Logout
# =========================
def user_logout(request):
    logout(request)
    return redirect('login')


# =========================
# Dashboard
# =========================
@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'resumes': resumes})


# =========================
# Create Resume
# =========================
from .models import Resume, Skill, Education, Experience, Certification, Project

@login_required
def create_resume(request):
    if request.method == "POST":

        resume = Resume.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            summary=request.POST.get('summary')
        )

        # Skills (comma separated)
        skills_data = request.POST.get('skills')
        if skills_data:
            for skill in skills_data.split(','):
                Skill.objects.create(
                    resume=resume,
                    name=skill.strip()
                )

        # Education (store full text as institution)
        education_data = request.POST.get('education')
        if education_data:
            Education.objects.create(
                resume=resume,
                institution=education_data,
                degree="",
                year=""
            )

        # Experience (store full text in description)
        experience_data = request.POST.get('experience')
        if experience_data:
            Experience.objects.create(
                resume=resume,
                company="",
                role="",
                start_date="",
                end_date="",
                description=experience_data
            )

        # Projects
        project_data = request.POST.get('projects')
        if project_data:
            Project.objects.create(
                resume=resume,
                title="Project",
                description=project_data
            )

        # Certifications
        cert_data = request.POST.get('certifications')
        if cert_data:
            Certification.objects.create(
                resume=resume,
                name=cert_data,
                issuer=""
            )

        return redirect('dashboard')

    return render(request, 'resumes/create_resume.html')


# =========================
# Export PDF (ReportLab)
# =========================
@login_required
def export_pdf(request, resume_id):
    resume = Resume.objects.get(id=resume_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # ===== Custom Styles =====
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=6
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=6
    )

    normal_style = styles["Normal"]

    # ===== HEADER (Name + Contact) =====
    elements.append(Paragraph(resume.full_name, name_style))
    elements.append(Paragraph(f"{resume.email} | {resume.phone}", contact_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.2 * inch))

    # ===== TITLE =====
    elements.append(Paragraph(resume.title, section_style))
    elements.append(Spacer(1, 0.15 * inch))

    # ===== SUMMARY =====
    elements.append(Paragraph("Professional Summary", section_style))
    elements.append(Paragraph(resume.summary, normal_style))

    # ===== SKILLS =====
    skills = Skill.objects.filter(resume=resume)
    if skills.exists():
        elements.append(Paragraph("Skills", section_style))
        skill_text = ", ".join([skill.name for skill in skills])
        elements.append(Paragraph(skill_text, normal_style))

    # ===== EDUCATION =====
    educations = Education.objects.filter(resume=resume)
    if educations.exists():
        elements.append(Paragraph("Education", section_style))
        for edu in educations:
            elements.append(Paragraph(edu.institution, normal_style))

    # ===== EXPERIENCE =====
    experiences = Experience.objects.filter(resume=resume)
    if experiences.exists():
        elements.append(Paragraph("Experience", section_style))
        for exp in experiences:
            elements.append(Paragraph(exp.description, normal_style))

    # ===== PROJECTS =====
    projects = Project.objects.filter(resume=resume)
    if projects.exists():
        elements.append(Paragraph("Projects", section_style))
        for project in projects:
            elements.append(Paragraph(project.description, normal_style))

    # ===== CERTIFICATIONS =====
    certifications = Certification.objects.filter(resume=resume)
    if certifications.exists():
        elements.append(Paragraph("Certifications", section_style))
        for cert in certifications:
            elements.append(Paragraph(cert.name, normal_style))

    doc.build(elements)
    return response