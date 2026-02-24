from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import Resume


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
@login_required
def create_resume(request):
    if request.method == "POST":
        title = request.POST['title']
        summary = request.POST['summary']

        Resume.objects.create(
            user=request.user,
            title=title,
            summary=summary
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

    p = canvas.Canvas(response, pagesize=letter)

    # Starting position
    y = 750

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, y, "Resume")
    y -= 40

    p.setFont("Helvetica", 12)
    p.drawString(100, y, f"Title: {resume.title}")
    y -= 25

    p.drawString(100, y, "Summary:")
    y -= 20

    # Wrap long summary text
    text_object = p.beginText(100, y)
    text_object.setFont("Helvetica", 12)

    for line in resume.summary.split('\n'):
        text_object.textLine(line)

    p.drawText(text_object)

    p.save()

    return response